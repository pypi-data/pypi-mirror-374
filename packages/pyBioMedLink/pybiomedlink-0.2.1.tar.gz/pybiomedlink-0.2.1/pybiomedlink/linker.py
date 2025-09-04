from abc import ABC, abstractmethod
from typing import List, Dict, Any
import random
import json

from tqdm.auto import tqdm
from rank_bm25 import BM25Okapi
import torch as th
from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM, GenerationConfig


class BaseZSLinker(ABC):
    """
    Base class for all zero-shot linkers.

    These linkers do not require training.
    """
    @abstractmethod
    def predict(self, query: str, top_k: int) -> List[str]:
        """
        Predict the top-k linked entities/labels for a given query.
        """
        pass

    @abstractmethod
    def predict_aux(self, query: str, top_k: int) -> Dict[str, Any]:
        """
        Predict auxiliary information for the query.
        This can include additional scores or other information.
        """
        pass


class RandomLinker(BaseZSLinker):
    """
    Random zero-shot linker.
    """
    def __init__(self, labels: List[str], seed: int = 42):
        """
        Args:
            labels (List[str]): List of labels/entities to link against.
        """
        self.labels = labels
        self.rng = random.Random(seed)  # fixed seed for reproducibility
    
    def predict(self, query: str, top_k: int) -> List[str]:
        """
        Predict the top-k linked entities/labels for a given query.
        """
        return self.rng.sample(self.labels, k=top_k)

    def predict_aux(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        preds = self.predict(query, top_k)
        result = {
            "labels": preds,
            "scores": [1.0 for i in top_k]
        }
        return result


class BM25Linker(BaseZSLinker):
    """
    BM25-based zero-shot linker.
    
    This linker uses the BM25 algorithm to link biomedical terms.
    """
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Tokenize the input text into a list of tokens.
        
        Args:
            text (str): The input text to tokenize.
        Returns:
            List[str]: A list of tokens.
        """
        # TODO: may use a more sophisticated tokenizer
        return text.split(" ")

    def __init__(self, labels: List[str]):
        """
        Args:
            labels (List[str]): List of labels/entities to link against.
        """
        tokenized_labels = [BM25Linker.tokenize(label) for label in labels]
        self.labels = labels
        self.model = BM25Okapi(tokenized_labels)

    def predict(self, query: str, top_k: int = 5) -> List[str]:
        """
        Predict the top-k linked entities for a given query.
        
        Args:
            query (str): The input query to link.
            top_k (int): The number of top results to return.
        Returns:
            List[str]: A list of top-k linked entities.
        """
        tokenized_query = BM25Linker.tokenize(query)
        return self.model.get_top_n(tokenized_query, self.labels, n=top_k)

    def predict_aux(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        tokenized_query = BM25Linker.tokenize(query)
        label_scores = self.model.get_scores(tokenized_query)
        top_indices = label_scores.argsort(stable=True)[-top_k:][::-1]
        result = {
            "labels": [self.labels[i] for i in top_indices],
            "scores": [label_scores[i].item() for i in top_indices]
        }
        return result


class LevenshteinLinker(BaseZSLinker):
    """
    Levenshtein distance-based zero-shot linker.
    
    This linker uses the Levenshtein distance to link biomedical terms.
    Implementation adapted from https://www.nltk.org/_modules/nltk/metrics/distance.html#edit_distance_align
    """
    @staticmethod
    def _edit_dist_init(len1: int, len2: int) -> List[List[int]]:
        lev = []
        for i in range(len1):
            lev.append([0] * len2)  # initialize 2D array to zero
        for i in range(len1):
            lev[i][0] = i  # column 0: 0,1,2,3,4,...
        for j in range(len2):
            lev[0][j] = j  # row 0: 0,1,2,3,4,...
        return lev
    
    @staticmethod
    def _last_left_t_init(sigma: str):
        return {c: 0 for c in sigma}
    
    @staticmethod
    def _edit_dist_step(
        lev: List[List[int]], 
        i: int, 
        j: int, 
        s1: str, 
        s2: str, 
        last_left: int, 
        last_right: int, 
        substitution_cost: int = 1, 
        transpositions: bool = False
    ):
        c1 = s1[i - 1]
        c2 = s2[j - 1]

        # skipping a character in s1
        a = lev[i - 1][j] + 1
        # skipping a character in s2
        b = lev[i][j - 1] + 1
        # substitution
        c = lev[i - 1][j - 1] + (substitution_cost if c1 != c2 else 0)

        # transposition
        d = c + 1  # never picked by default
        if transpositions and last_left > 0 and last_right > 0:
            d = lev[last_left - 1][last_right - 1] + i - last_left + j - last_right - 1

        # pick the cheapest
        lev[i][j] = min(a, b, c, d)
    
    @staticmethod
    def edit_distance(
        s1: str, 
        s2: str, 
        substitution_cost: int = 1, 
        transpositions: bool = False):
        """
        Calculate the Levenshtein edit-distance between two strings.
        The edit distance is the number of characters that need to be
        substituted, inserted, or deleted, to transform s1 into s2.  For
        example, transforming "rain" to "shine" requires three steps,
        consisting of two substitutions and one insertion:
        "rain" -> "sain" -> "shin" -> "shine".  These operations could have
        been done in other orders, but at least three steps are needed.

        Allows specifying the cost of substitution edits (e.g., "a" -> "b"),
        because sometimes it makes sense to assign greater penalties to
        substitutions.

        This also optionally allows transposition edits (e.g., "ab" -> "ba"),
        though this is disabled by default.

        :param s1, s2: The strings to be analysed
        :param transpositions: Whether to allow transposition edits
        :type s1: str
        :type s2: str
        :type substitution_cost: int
        :type transpositions: bool
        :rtype: int
        """
        # set up a 2-D array
        len1 = len(s1)
        len2 = len(s2)
        lev = LevenshteinLinker._edit_dist_init(len1 + 1, len2 + 1)

        # retrieve alphabet
        sigma = set()
        sigma.update(s1)
        sigma.update(s2)

        # set up table to remember positions of last seen occurrence in s1
        last_left_t = LevenshteinLinker._last_left_t_init(sigma)

        # iterate over the array
        # i and j start from 1 and not 0 to stay close to the wikipedia pseudo-code
        # see https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance
        for i in range(1, len1 + 1):
            last_right_buf = 0
            for j in range(1, len2 + 1):
                last_left = last_left_t[s2[j - 1]]
                last_right = last_right_buf
                if s1[i - 1] == s2[j - 1]:
                    last_right_buf = j
                LevenshteinLinker._edit_dist_step(
                    lev,
                    i,
                    j,
                    s1,
                    s2,
                    last_left,
                    last_right,
                    substitution_cost=substitution_cost,
                    transpositions=transpositions,
                )
            last_left_t[s1[i - 1]] = i
        return lev[len1][len2]

    def __init__(self, labels: List[str]):
        """
        Args:
            labels (List[str]): List of labels/entities to link against.
        """
        self.labels = labels
    
    def predict(self, query: str, top_k: int = 5) -> List[str]:
        """
        lev_distances = [
            (label, LevenshteinLinker.edit_distance(query, label))
            for label in self.labels
        ]
        # Sort by distance, ascending
        lev_distances.sort(key=lambda x: x[1])
        # Return the top-k labels
        return [label for label, _ in lev_distances[:top_k]]
        """
        results = self.predict_aux(query, top_k)
        return results["labels"]

    def predict_aux(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        lev_distances = [
            (label, LevenshteinLinker.edit_distance(query, label))
            for label in self.labels
        ]
        # Sort by distance, ascending
        lev_distances.sort(key=lambda x: x[1])
        results = {
            "labels": [label for label, _ in lev_distances[:top_k]],
            "scores": [distance for _, distance in lev_distances[:top_k]]
        }
        return results


class TransformerEmbLinker(BaseZSLinker):
    """
    Transformer-based zero-shot linker.
    """
    def __init__(
            self, 
            labels: List[str],
            model_name: str = "cambridgeltl/SapBERT-from-PubMedBERT-fulltext", 
            batch_size: int = 16
        ):
        # prepare models
        self.device = th.device("cuda" if th.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        print(f'Using device: {self.device}. Model: {model_name} loaded.')
        # prepare embeddings of labels
        self.labels = labels
        self.label_embs = []
        self.bs = batch_size
        for i in tqdm(range(0, len(labels), self.bs)):
            batch = labels[i : i + self.bs]
            outputs = self._get_embs(batch)
            self.label_embs.append(outputs.last_hidden_state[:, 0, :].cpu().detach())
        self.label_embs = th.cat(self.label_embs, dim=0)
        print(f'Label embs shape: {self.label_embs.shape}')

    def _get_embs(self, batch: List[str]) -> th.Tensor:
        assert isinstance(batch, list), "Input batch must be a list of strings."
        inputs = self.tokenizer(batch, padding=True, truncation=False, return_tensors="pt").to(self.device)
        with th.inference_mode():
            outputs = self.model(**inputs)
        return outputs
        
    def predict(self, query: str, top_k: int = 5) -> List[str]:
        results = self.predict_aux(query, top_k)
        return results["labels"]
        
    def predict_aux(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        query_emb = self._get_embs([query]).last_hidden_state[:, 0, :].cpu().detach()  # shape: (1, emb_dim)
        # Calculate cosine similarities
        similarities = th.nn.functional.cosine_similarity(query_emb, self.label_embs)   # shape: (num_labels,)
        # Get top-k indices
        topk_ret = th.topk(similarities, k=top_k)
        results = {
            "labels": [self.labels[i] for i in topk_ret.indices],
            "scores": topk_ret.values.cpu().tolist()
        }
        return results


class Qwen3PromptLinker(BaseZSLinker):
    """
    Language Model Prompt-based zero-shot linker.
    
    This linker uses a language model and pre-defined prompts for linking biomedical terms.
    """
    @staticmethod
    def GO_BioDomainPrompt(query: str, labels: List[str], top_k: int) -> str:
        """
        Generate a prompt for the GO BioDomain task.
        
        Args:
            query (str): The input query to link.
            labels (List[str]): List of labels/entities to link against.
        Returns:
            str: The generated prompt.
        """
        domains_str = "\n".join(f"- {d}" for d in labels)
        prompt = f"""You are a biomedical ontology expert.  
Below is a GO term.  
From the list of Biodomains, choose the **top {top_k}** labels that best fit this term—ranked most-to-least appropriate.  
**Do not** ever reply “Unknown”, and **do not** return more or fewer than five.  
**List only** the domain names, **without** any numbering, bullets, or additional text.

**Biodomain options:**
{domains_str}

**GO Term:** {query}  

**Output** your answer strictly in the following JSON format, in descending order of relevance:
["Domain1", "Domain2", ..., "Domain{top_k}"]
"""
        return prompt

    def __init__(self, labels: List[str], model_name: str = 'Qwen/Qwen3-0.6B'):
        assert model_name.startswith("Qwen"), "Model name must start with 'Qwen'"
        self.labels = labels
        self.model_name = model_name
        # Initialize the model and tokenizer here if needed
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto"
        )
        self.model.eval()
        self.max_new_tokens = 32768
        print(f'Model {model_name} loaded for LMPromptLinker.')

    def predict(
            self, 
            query: str, 
            top_k: int = 5, 
            prompt_template: str = "GO_BioDomainPrompt",
            enable_thinking: bool = True,
        ) -> List[str]:
        results = self.predict_aux(query, top_k, prompt_template, enable_thinking)
        return results["labels"]


    def predict_aux(
            self, 
            query: str, 
            top_k: int = 5,
            prompt_template: str = "GO_BioDomainPrompt",
            enable_thinking: bool = True,
        ) -> Dict[str, Any]:
        """
        LLM can not return a list of labels with **scores**.
        """
        # TODO: support user-defined prompts
        if prompt_template == "GO_BioDomainPrompt":
            prompt = self.GO_BioDomainPrompt(query, self.labels, top_k)
        else:
            raise ValueError(f"Unknown prompt template: {prompt_template}")
        #print(f'Generated prompt:\n{prompt}')
        # prepare arguments
        model = self.model
        tokenizer = self.tokenizer
        max_new_tokens = self.max_new_tokens
        # do inference
        messages = [
            {"role": "user", "content": prompt}
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=enable_thinking
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
        # best practise params:
        if enable_thinking == True:
            generation_config = model.generation_config
        else:
            generation_config = model.generation_config
            generation_config.temperature = 0.7
            generation_config.top_p = 0.8
            generation_config.top_k = 20
            generation_config.min_probability = 0.0

        # conduct text completion
        with th.inference_mode():
            generated_ids = model.generate(
                **model_inputs,
                max_new_tokens=max_new_tokens,
                generation_config=generation_config,
            )
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

        # parsing thinking content
        try:
            # rindex finding 151668 (</think>)
            index = len(output_ids) - output_ids[::-1].index(151668)
        except ValueError:
            index = 0

        thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
        content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
        #print("thinking content:", thinking_content)
        #print("content:", content)

        # parse the content
        error_msg = ""
        try:
            parsed_content = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON content: {e}")
            parsed_content = []
            error_msg = str(e)
        
        results = {
            "labels": parsed_content,
            "thinking_content": thinking_content,
            "content": content,
            "error_msg": error_msg
        }
        return results