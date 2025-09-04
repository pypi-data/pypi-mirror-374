# type: ignore
import torch  # type: ignore
import torch.nn as nn  # type: ignore
from torch.utils.data import Dataset, DataLoader  # type: ignore
from transformers import AutoTokenizer, AutoModel, Trainer, TrainingArguments  # type: ignore
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
from sklearn.model_selection import train_test_split  # type: ignore
from sklearn.metrics import accuracy_score, f1_score  # type: ignore
import json


class CodeSentimentDataset(Dataset):
    def __init__(self, codes, labels, tokenizer, max_length=512):
        self.codes = codes
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.codes)
    
    def __getitem__(self, idx):
        code = str(self.codes[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            code,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }


class CodeSentimentModel(nn.Module):
    def __init__(self, model_name="microsoft/codebert-base", num_classes=2):
        super().__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_classes)
        
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        output = self.dropout(pooled_output)
        return self.classifier(output)


class CodeSentimentTrainer:
    def __init__(self, model_name="microsoft/codebert-base"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = None
        
    def load_dataset(self, dataset_path: str):
        """Load dataset from JSON file"""
        with open(dataset_path, 'r') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        
        # Convert sentiment labels to numeric
        df['label_numeric'] = (df['sentiment_label'] == 'positive').astype(int)
        
        return df['code'].tolist(), df['label_numeric'].tolist()
    
    def train(self, dataset_path: str, output_dir: str = "./code_sentiment_model"):
        """Train the model"""
        
        # Load data
        codes, labels = self.load_dataset(dataset_path)
        
        # Split data
        train_codes, val_codes, train_labels, val_labels = train_test_split(
            codes, labels, test_size=0.2, random_state=42
        )
        
        # Create datasets
        train_dataset = CodeSentimentDataset(train_codes, train_labels, self.tokenizer)
        val_dataset = CodeSentimentDataset(val_codes, val_labels, self.tokenizer)
        
        # Initialize model
        self.model = CodeSentimentModel(self.model_name)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir='./logs',
            logging_steps=100,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
        )
        
        # Custom trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=self.compute_metrics,
        )
        
        # Train
        trainer.train()
        
        # Save model
        trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        print(f"Model saved to {output_dir}")
    
    def compute_metrics(self, eval_pred):
        """Compute metrics for evaluation"""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        return {
            'accuracy': accuracy_score(labels, predictions),
            'f1': f1_score(labels, predictions, average='weighted')
        }
    
    def evaluate_model(self, test_codes: list, test_labels: list):
        """Evaluate trained model"""
        if not self.model:
            raise ValueError("Model not trained yet")
        
        test_dataset = CodeSentimentDataset(test_codes, test_labels, self.tokenizer)
        test_loader = DataLoader(test_dataset, batch_size=8)
        
        self.model.eval()
        predictions = []
        
        with torch.no_grad():
            for batch in test_loader:
                outputs = self.model(
                    input_ids=batch['input_ids'],
                    attention_mask=batch['attention_mask']
                )
                preds = torch.argmax(outputs, dim=1)
                predictions.extend(preds.cpu().numpy())
        
        accuracy = accuracy_score(test_labels, predictions)
        f1 = f1_score(test_labels, predictions, average='weighted')
        
        return {'accuracy': accuracy, 'f1': f1}


# Lightweight alternative using scikit-learn
class LightweightCodeClassifier:
    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.ensemble import RandomForestClassifier
        
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        
    def train(self, codes: list, labels: list):
        """Train lightweight model"""
        # Convert code to features
        X = self.vectorizer.fit_transform(codes)
        
        # Train classifier
        self.classifier.fit(X, labels)
        
        print("Lightweight model trained successfully")
    
    def predict(self, code: str) -> dict:
        """Predict sentiment for code"""
        X = self.vectorizer.transform([code])
        prediction = self.classifier.predict(X)[0]
        probability = self.classifier.predict_proba(X)[0].max()
        
        return {
            'label': 'positive' if prediction == 1 else 'negative',
            'confidence': probability
        }


if __name__ == "__main__":
    # Example usage
    trainer = CodeSentimentTrainer()
    
    # Train transformer model (requires GPU for reasonable speed)
    # trainer.train("code_sentiment_dataset.json")
    
    # Or use lightweight alternative
    lightweight = LightweightCodeClassifier()
    
    # Load sample data
    sample_codes = [
        "def clean_function(): return [x for x in items]",
        "# TODO: fix this ugly hack\nglobal x\nx = 123"
    ]
    sample_labels = [1, 0]  # positive, negative
    
    lightweight.train(sample_codes, sample_labels)
    
    # Save model for automatic loading
    import pickle
    from pathlib import Path
    
    models_dir = Path(__file__).parent.parent / "codemood" / "models"
    models_dir.mkdir(exist_ok=True)
    
    model_path = models_dir / "code_sentiment.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(lightweight, f)
    
    print(f"✅ Model saved to {model_path}")
    print("🔄 Restart Python to load the new model")
    
    # Test prediction
    result = lightweight.predict("def elegant_code(): pass")
    print(f"Prediction: {result}")