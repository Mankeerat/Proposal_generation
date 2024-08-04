#%%
LONG_ARTICLE = """" Type something

"""

from transformers import LEDForConditionalGeneration, LEDTokenizer
import torch

tokenizer = LEDTokenizer.from_pretrained("allenai/led-large-16384-arxiv")

input_ids = tokenizer(LONG_ARTICLE, return_tensors="pt").input_ids.to("cuda")
global_attention_mask = torch.zeros_like(input_ids)
# set global_attention_mask on first token
global_attention_mask[:, 0] = 1

model = LEDForConditionalGeneration.from_pretrained("allenai/led-large-16384-arxiv", return_dict_in_generate=True).to("cuda")

sequences = model.generate(input_ids, global_attention_mask=global_attention_mask).sequences

summary = tokenizer.batch_decode(sequences)
print(summary)
