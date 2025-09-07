from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import PPOTrainer, PPOConfig
import torch

class STVTrainer:
    def __init__(self, model_name="nousresearch/deephermes-3-mistral-24b-preview:free"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.config = PPOConfig()
        self.trainer = PPOTrainer(self.model, self.tokenizer, **self.config.__dict__)

    def fine_tune(self, prompt, responses, epochs=1):
        '''
        prompt: list of input texts (str)
        responses: list of expected responses (str)
        epochs: số lần train lại
        '''
        for _ in range(epochs):
            for q, a in zip(prompt, responses):
                # encode input
                inputs = self.tokenizer(q, return_tensors="pt")
                outputs = self.tokenizer(a, return_tensors="pt")
                # fine-tune logic (ví dụ giả lập PPO)
                self.trainer.step(inputs.input_ids, outputs.input_ids)
        print("Fine-tune hoàn thành!")