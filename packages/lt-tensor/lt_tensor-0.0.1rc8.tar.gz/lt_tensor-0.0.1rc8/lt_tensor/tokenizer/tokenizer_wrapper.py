__all__ = ["TokenizerWP"]
from lt_utils.file_ops import is_path_valid, find_files
from lt_utils.common import *
import torch
from torch import Tensor
from functools import lru_cache
from torch.nn import functional as F


from tokenizers import Tokenizer
from tokenizers.models import BPE
from .utils import get_phonetic_tokens, get_default_tokens


class TokenizerWP:
    special_tokens = {
        "pad": "<pad>",  # id 0
        "unk": "<unk>",  # id 1
        "sep": "<sep>",  # id 2
        "bos": "<s>",  # id 3
        "eos": "</s>",  # id 4
        "mask": "<mask>",  # id 5
        "cls": "<cls>",  # id 6
    }

    def __init__(
        self,
        tokenizer_or_file: Union[Tokenizer, str, Path],
        total_added_special_tokens: int = 0,
    ):
        if isinstance(tokenizer_or_file, (str, Path)):
            self._load_from_file(tokenizer_or_file)
        else:
            self.tokenizer: Tokenizer = tokenizer_or_file
            self._post_process_setup()

        self.special_tokens_range = 7 + int(max(total_added_special_tokens, 0))
        # keeping those pre-computed
        self.pad_token_id: int = 0
        self.unk_token_id: int = 1
        self.sep_token_id: int = 2
        self.bos_token_id: int = 3
        self.eos_token_id: int = 4
        self.mask_token_id: int = 5
        self.cls_token_id: int = 6

        self.pad_token: Tensor = torch.tensor([[self.pad_token_id]], dtype=torch.long)
        self.unk_token: Tensor = torch.tensor([[self.unk_token_id]], dtype=torch.long)
        self.sep_token: Tensor = torch.tensor([[self.sep_token_id]], dtype=torch.long)
        self.bos_token: Tensor = torch.tensor([[self.bos_token_id]], dtype=torch.long)
        self.eos_token: Tensor = torch.tensor([[self.eos_token_id]], dtype=torch.long)
        self.mask_token: Tensor = torch.tensor([[self.mask_token_id]], dtype=torch.long)
        self.cls_token: Tensor = torch.tensor([[self.cls_token_id]], dtype=torch.long)

        self.pad_text: str = "<pad>"
        self.unk_text: str = "<unk>"
        self.sep_text: str = "<sep>"
        self.bos_text: str = "<s>"
        self.eos_text: str = "</s>"
        self.mask_text: str = "<mask>"
        self.cls_text: str = "<cls>"

        self.special_vocab = {
            self.pad_token_id: self.pad_text,
            self.unk_token_id: self.unk_text,
            self.sep_token_id: self.sep_text,
            self.bos_token_id: self.bos_text,
            self.eos_token_id: self.eos_text,
            self.mask_token_id: self.mask_text,
            self.cls_token_id: self.cls_text,
        }

    @property
    def vocab_size(self):
        return self.tokenizer.get_vocab_size()

    def __len__(self):
        return self.vocab_size

    def encode(
        self,
        texts: Union[str, List[str]],
        add_bos_token: bool = False,
        add_eos_token: bool = False,
        padding: bool = False,
        truncation: Union[bool, str, None] = None,
        max_size: Optional[int] = None,
        truncation_direction: Literal["left", "right"] = "left",
        padding_from: Literal["left", "right"] = "right",
    ) -> Union[Tensor, List[Tensor]]:
        assert isinstance(texts, (str, list, tuple)) and texts
        _kw_unit = dict(
            add_bos=add_bos_token,
            add_eos=add_eos_token,
            max_size=max_size if truncation else None,
            truncation=truncation_direction,
        )
        if isinstance(texts, str):
            result = self._encode_unit(texts, **_kw_unit)
            if max_size and padding:
                return self.pad(
                    [result], from_left=padding_from == "left", to_size=max_size
                )
            return result.view(1, result.shape[-1])
        # else:
        B = len(texts)
        tokens = [self._encode_unit(x, **_kw_unit) for x in texts]
        if padding:
            return self.pad(tokens, from_left=padding_from == "left", to_size=max_size)
        return tokens

    def decode(
        self,
        tokenized: Union[int, list[Tensor], List[int], Tensor],
        return_special_tokens: bool = False,
    ):
        B = 1
        tok_kwargs = dict(return_special_tokens=return_special_tokens)

        if isinstance(tokenized, Tensor):
            if tokenized.ndim > 1:
                B = tokenized.shape[0]

        elif isinstance(tokenized, (list, tuple)):
            if not tokenized:
                return ""
            if isinstance(tokenized[0], Tensor):
                assert all(
                    list(map(lambda x: isinstance(x, Tensor), tokenized))
                ), "Not all items provided in the list is a valid tensor"
                B = len(tokenized)
                if B == 1:
                    tokenized = tokenized[0]
            else:
                assert all(
                    list(map(lambda x: isinstance(x, int), tokenized))
                ), "Not all items provided in the list is a valid token"

        if B == 1:
            return self._decode(tokenized, **tok_kwargs)
        return [self._decode(tokenized[i], **tok_kwargs) for i in range(B)]

    def pad(
        self,
        input_ids: list[Tensor],
        from_left: bool = False,
        to_size: Optional[int] = None,
    ):
        assert input_ids, "No value has been provided!"
        if len(input_ids) > 1:
            largest_text = max([x.size(-1) for x in input_ids])
            if to_size:
                largest_text = max(largest_text, to_size)
            if from_left:
                fn = lambda x: (largest_text - x.size(-1), 0)
            else:
                fn = lambda x: (0, largest_text - x.size(-1))
        else:
            if not to_size or to_size <= input_ids[0].shape[-1]:
                return input_ids[0].view(1, input_ids[0].shape[-1])
            if from_left:
                fn = lambda x: (to_size - x.size(-1), 0)
            else:
                fn = lambda x: (0, to_size - x.size(-1))
            return F.pad(
                input_ids[0],
                pad=fn(input_ids[0]),
                mode="constant",
                value=self.pad_token_id,
            ).view(1, to_size)
        B = len(input_ids)
        return torch.stack(
            [
                F.pad(
                    x,
                    pad=fn(x),
                    mode="constant",
                    value=self.pad_token_id,
                )
                for x in input_ids
            ],
            dim=0,
        ).view(B, largest_text)

    def _encode_output_processor(self, output: List[int]):
        return torch.tensor([output], dtype=torch.long)

    @lru_cache(maxsize=65536)
    def _dec_id(self, token: int, return_special_tokens: bool = False):
        if token < self.special_tokens_range:
            if not return_special_tokens:
                return ""
            return self.special_vocab.get(token, self.unk_text)
        return self._dec_vocab.get(
            token,
            self.unk_text if return_special_tokens else "",
        )

    def _encode_unit(
        self,
        text: str,
        add_bos: bool,
        add_eos: bool,
        max_size: Optional[int] = None,
        truncation: Literal["left", "right"] = "left",
        **kwargs,
    ):
        tokens = self.tokenizer.encode(text, add_special_tokens=False).ids
        _length = len(tokens)
        if max_size is not None:
            _extra = int(add_bos) + int(add_eos)

            if truncation and (_length + _extra) > max_size:
                if truncation == "left":
                    tokens = tokens[-(max_size - _extra) :]
        if add_bos:
            tokens.insert(0, self.bos_token_id)
        if add_eos:
            tokens.append(self.eos_token_id)
        return torch.tensor([tokens], dtype=torch.long)

    def _decode(
        self,
        tokens: Union[List[int], Tensor],
        return_special_tokens: bool = False,
    ):
        if isinstance(tokens, Tensor):
            tokens = tokens.flatten().tolist()
        return "".join(
            [
                self._dec_id(tok, return_special_tokens)
                for tok in tokens
                if isinstance(tok, int)
            ]
        )

    def _post_process_setup(self):
        self._dec_vocab = {
            value: txt for txt, value in self.tokenizer.get_vocab().items()
        }

    def _load_from_file(self, path: Union[str, Path]):
        is_path_valid(path, validate=True)
        if Path(path).is_dir():
            path = find_files(path, "*tokenizer*.json")
            assert path, f"No tokenizer was located in the given path '{str(path)}'"
            path = path[0]
        path = Path(path)
        self.tokenizer = Tokenizer.from_file(str(path))
        self._post_process_setup()

    @classmethod
    def create_tokenizer(
        cls,
        tokens: List[str] = get_default_tokens(),
        reserved_token: int = 30,
        save_location: Optional[Union[str, Path]] = None,
    ):
        special_tokens = {
            "pad": "<pad>",  # id 0
            "unk": "<unk>",  # id 1
            "sep": "<sep>",  # id 2
            "bos": "<s>",  # id 3
            "eos": "</s>",  # id 4
            "mask": "<mask>",  # id 5
            "cls": "<cls>",  # id 6
        }
        for i in range(reserved_token):
            special_tokens[f"<|reserved_{i}|>"] = f"<|reserved_{i}|>]"

        vocab = {}
        for idx, tokenizer in enumerate(special_tokens.values()):
            vocab[tokenizer] = idx
        for i, tokenizer in enumerate(
            tokens + ["▁", "Ġ"], start=len(special_tokens) - 1
        ):
            vocab[tokenizer] = i

        tokenizer = Tokenizer(BPE(vocab=vocab, merges=[]))
        if save_location is not None:
            if not Path(save_location).name.endswith(".json"):
                save_location = Path(save_location, "tokenizer.json")
            Path(save_location).parent.mkdir(exist_ok=True, parents=True)
            tokenizer.save(str(save_location), pretty=True)
        else:
            print(
                "Tokenizer was created but not saved, you can save it by using 'save_tokenizer(folder location)' to store it."
            )
        return cls(tokenizer)
