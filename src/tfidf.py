import re
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class TFIDFCalculator:
    """
    Implements TF-IDF weighting for code modifications.
    TREC-style term weighting adapted for source code.
    """
    def __init__(self):
        # Custom tokenizer for code: splits on non-alphanumeric, keeps underscores
        token_pattern = r"(?u)\b\w\w+\b" 
        self.vectorizer = TfidfVectorizer(
            token_pattern=token_pattern,
            stop_words='english', # TODO: Add code-specific stopwords (if, else, return)
            max_features=1000 # Limit feature space for performance
        )
        self.is_fitted = False

    def _preprocess_patch(self, patch: str) -> str:
        """
        Cleans the git patch to extract only added/modified lines.
        Ignores removed lines (-) and metadata (@@).
        """
        if not patch:
            return ""
        
        relevant_text = []
        for line in patch.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                relevant_text.append(line[1:]) # Remove the '+' marker
        return " ".join(relevant_text)

    def fit_corpus(self, commits: list[dict]):
        """
        Fits the TF-IDF model on the corpus of all commit patches.
        commits: List of dicts with 'files' -> [{'patch': ...}]
        """
        corpus = []
        for commit in commits:
            commit_text = ""
            for f in commit.get('files', []):
                commit_text += " " + self._preprocess_patch(f.get('patch_content', ''))
            corpus.append(commit_text)
            
        if not corpus or len(corpus) == 0:
            print("Warning: Empty corpus for TF-IDF")
            return

        try:
            self.vectorizer.fit(corpus)
            self.is_fitted = True
        except ValueError:
            print("Warning: TF-IDF Vocabulary Empty (only stop words or empty patches). Using baseline weights.")
            self.is_fitted = False

    def compute_weight(self, patch_content: str) -> float:
        """
        Calculates the aggregate TF-IDF score for a specific file patch.
        Returns a normalized weight (0.0 - 1.0) indicating semantic richness.
        """
        if not self.is_fitted or not patch_content:
            return 0.1 # Baseline weight for empty/non-fitted
            
        cleaned_text = self._preprocess_patch(patch_content)
        if not cleaned_text.strip():
            return 0.1
            
        tfidf_matrix = self.vectorizer.transform([cleaned_text])
        
        # Mathematical Logic:
        # We sum the TF-IDF scores of all terms in the patch.
        # This represents the "Total Information Content" of the change.
        total_score = np.sum(tfidf_matrix.data)
        
        # Log-normalization to squash extreme values (large refactors) into 0-1 range
        # We use a gentle squash so small diffs still register.
        weight = np.log1p(total_score) # log(1+x)
        
        # Normalize to typical range [0, 1] essentially
        # For a single unique term, score ~1.0 -> weight ~0.69
        # For huge diffs, score ~100 -> weight ~4.6. We clip at 1.0.
        
        # We want to distinguish ANY match (>0) from NO match (0).
        # So we clip lower bound very low, or handling 0 separately.
        
        final_weight = min(1.0, max(0.01, weight))
        return final_weight
