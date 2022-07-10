from typing import List, Tuple

import torch
from comer.datamodule import vocab
from torch import FloatTensor, LongTensor


# modified from
# https://github.com/huggingface/transformers/blob/af6e01c5bc39467f1e3ce47a2135fb1777af1db2/src/transformers/generation_beam_search.py#L206
class BeamSearchScorer:
    def __init__(
        self,
        batch_size: int,
        beam_size: int,
        alpha: float,
        do_early_stopping: bool,
        device: torch.device,
    ) -> None:
        self.batch_size = batch_size
        self.beam_size = beam_size
        self.alpha = alpha
        self.device = device

        self._beam_hyps = [
            BeamHypotheses(beam_size, alpha, do_early_stopping)
            for _ in range(batch_size)
        ]

        self._done = torch.tensor(
            [False for _ in range(batch_size)], dtype=torch.bool, device=self.device
        )

    def is_done(self) -> bool:
        return self._done.all()

    def process(
        self,
        input_ids: LongTensor,
        next_scores: FloatTensor,
        next_tokens: LongTensor,
        next_indices: LongTensor,
    ) -> Tuple[FloatTensor, LongTensor, LongTensor]:
        """score for each beam

        Parameters
        ----------
        input_ids : LongTensor
            [b * beam_size, l]
        next_scores : FloatTensor
            [b, 2 * beam_size]
        next_tokens : LongTensor
            [b, 2 * beam_size]
        next_indices : LongTensor
            [b, 2 * beam_size]

        Returns
        -------
        Tuple[FloatTensor, LongTensor, LongTensor]
            next_scores: [b * beam_size]
            next_tokens: [b * beam_size]
            next_indices: [b * beam_size]
        """
        next_beam_scores = torch.zeros(
            (self.batch_size, self.beam_size),
            dtype=next_scores.dtype,
            device=self.device,
        )
        next_beam_tokens = torch.zeros(
            (self.batch_size, self.beam_size),
            dtype=next_tokens.dtype,
            device=self.device,
        )
        next_beam_indices = torch.zeros(
            (self.batch_size, self.beam_size),
            dtype=next_indices.dtype,
            device=self.device,
        )

        for batch_idx, beam_hyp in enumerate(self._beam_hyps):
            if self._done[batch_idx]:
                assert len(beam_hyp) >= self.beam_size
                # pad the batch
                next_beam_scores[batch_idx, :] = 0
                next_beam_tokens[batch_idx, :] = vocab.PAD_IDX
                next_beam_indices[batch_idx, :] = batch_idx * self.beam_size
                continue

            beam_idx = 0
            for beam_token_rank, (next_score, next_token, next_index) in enumerate(
                zip(
                    next_scores[batch_idx],
                    next_tokens[batch_idx],
                    next_indices[batch_idx],
                )
            ):
                batch_beam_idx = batch_idx * self.beam_size + next_index
                l2r_done = (
                    input_ids[batch_beam_idx][0].item() == vocab.SOS_IDX
                    and next_token.item() == vocab.EOS_IDX
                )
                r2l_done = (
                    input_ids[batch_beam_idx][0].item() == vocab.EOS_IDX
                    and next_token.item() == vocab.SOS_IDX
                )
                if l2r_done or r2l_done:
                    if beam_token_rank >= self.beam_size:
                        # if beam_token does not belong to top num_beams tokens, it should not be added
                        continue
                    beam_hyp.add(input_ids[batch_beam_idx].clone(), next_score.item())
                else:
                    # add next predicted token since it is not eos_token
                    next_beam_scores[batch_idx, beam_idx] = next_score
                    next_beam_tokens[batch_idx, beam_idx] = next_token
                    next_beam_indices[batch_idx, beam_idx] = batch_beam_idx
                    beam_idx += 1

                # once the beam for next step is full, don't add more tokens to it.
                if beam_idx == self.beam_size:
                    break

            assert beam_idx == self.beam_size

            self._done[batch_idx] = beam_hyp.is_done(
                best_sum_logprobs=next_beam_scores[batch_idx].max().item(),
                cur_len=input_ids.shape[-1],
            )

        return (
            next_beam_scores.view(-1),
            next_beam_tokens.view(-1),
            next_beam_indices.view(-1),
        )

    def finalize(
        self,
        input_ids: LongTensor,
        final_scores: FloatTensor,
    ) -> Tuple[List[LongTensor], FloatTensor]:
        """generate final output

        Parameters
        ----------
        input_ids : LongTensor
            [b * beam_size, l]
        final_scores : FloatTensor
            [b * beam_size]

        Returns
        -------
        Tuple[List[LongTensor], FloatTensor]
            List[LongTensor]: [b * beam_size] without SOS or EOS token
            FloatTensor: [b * beam_size] corresponding scores
        """
        # finalize all open beam hypotheses and add to generated hypotheses
        for batch_idx, beam_hyp in enumerate(self._beam_hyps):
            if self._done[batch_idx]:
                continue

            # all open beam hypotheses are added to the beam hypothesis
            # beam hypothesis class automatically keeps the best beams
            for beam_id in range(self.beam_size):
                batch_beam_idx = batch_idx * self.beam_size + beam_id
                final_score = final_scores[batch_beam_idx].item()
                final_tokens = input_ids[batch_beam_idx]
                beam_hyp.add(final_tokens, final_score)

        all_hyps: List[LongTensor] = []
        scores: FloatTensor = torch.zeros(
            self.batch_size * self.beam_size, dtype=torch.float, device=self.device
        )

        for beam_hyp in self._beam_hyps:
            for score, seq in beam_hyp.beams:
                scores[len(all_hyps)] = score
                all_hyps.append(seq[1:])

        return all_hyps, scores


class BeamHypotheses:
    def __init__(self, num_beams: int, length_penalty: float, early_stopping: bool):
        """
        Initialize n-best list of hypotheses.
        """
        self.length_penalty = length_penalty
        self.early_stopping = early_stopping
        self.num_beams = num_beams
        self.beams: List[Tuple[float, LongTensor]] = []
        self.worst_score = 1e9

    def __len__(self):
        """
        Number of hypotheses in the list.
        """
        return len(self.beams)

    def add(self, hyp: LongTensor, sum_logprobs: float):
        """
        Add a new hypothesis to the list.
        """
        # if not _check_hypothesis_bracket(tuple(hyp.tolist())):
        #     sum_logprobs = float("-inf")

        score = sum_logprobs / (hyp.shape[-1] ** self.length_penalty)
        if len(self) < self.num_beams or score > self.worst_score:
            self.beams.append((score, hyp))
            if len(self) > self.num_beams:
                sorted_next_scores = sorted(
                    [(s, idx) for idx, (s, _) in enumerate(self.beams)]
                )
                del self.beams[sorted_next_scores[0][1]]
                self.worst_score = sorted_next_scores[1][0]
            else:
                self.worst_score = min(score, self.worst_score)

    def is_done(self, best_sum_logprobs: float, cur_len: int) -> bool:
        """
        If there are enough hypotheses and that none of the hypotheses being generated can become better than the worst
        one in the heap, then we are done with this sentence.
        """

        if len(self) < self.num_beams:
            return False
        elif self.early_stopping:
            return True
        else:
            cur_score = best_sum_logprobs / cur_len ** self.length_penalty
            ret = self.worst_score >= cur_score
            return ret
