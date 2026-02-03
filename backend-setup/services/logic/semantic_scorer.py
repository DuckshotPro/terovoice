|import logging
import time
from typing import List, Tuple, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("semantic-scorer")

class SemanticIntentScorer:
    """
    Local micro-model for sub-second intent classification.
    Uses quantized embeddings for speed.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the scorer.
        
        Args:
            model_name: HuggingFace model name (default: fast & small)
        """
        self.model_name = model_name
        self.model = None
        self.intent_embeddings = {}
        self.intent_labels = []
        self._load_model()

    def _load_model(self):
        """Lazy load the model to avoid blocking valid imports if libs missing."""
        try:
            logger.info(f"Loading semantic model: {self.model_name}...")
            start = time.time()
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded in {time.time() - start:.2f}s")
        except Exception as e:
            logger.error(f"Failed to load semantic model: {e}")
            self.model = None

    def register_intents(self, intents: Dict[str, List[str]]):
        """
        Pre-compute embeddings for intent phrases.
        
        Args:
            intents: Dict mapping IntentLabel -> [List of phrases]
            Example: {"EMERGENCY": ["I'm in pain", "It hurts bad"]}
        """
        if not self.model:
            return

        self.intent_embeddings = {}
        self.intent_labels = []
        
        all_phrases = []
        temp_labels = []

        for label, phrases in intents.items():
            for phrase in phrases:
                all_phrases.append(phrase)
                temp_labels.append(label)
        
        if not all_phrases:
            return

        # Batch encode all phrases
        embeddings = self.model.encode(all_phrases)
        
        self.intent_embeddings = embeddings
        self.intent_labels = temp_labels
        logger.info(f"Registered {len(all_phrases)} phrases for {len(intents)} intents.")

    def score(self, text: str, threshold: float = 0.75) -> Tuple[str, float]:
        """
        Score incoming text against registered intents.
        
        Returns:
            (Best Intent Label, Confidence Score)
            Returns ("None", 0.0) if below threshold or model not loaded.
        """
        if not self.model or len(self.intent_labels) == 0:
            return "None", 0.0

        # Encode input text
        input_vec = self.model.encode([text])
        
        # Calc cosine similarity
        # input_vec is (1, 384), intent_embeddings is (N, 384)
        sim_scores = cosine_similarity(input_vec, self.intent_embeddings)[0]
        
        best_idx = np.argmax(sim_scores)
        best_score = float(sim_scores[best_idx])
        
        if best_score >= threshold:
            best_label = self.intent_labels[best_idx]
            return best_label, best_score
        
        return "None", best_score
