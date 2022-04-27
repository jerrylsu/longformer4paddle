# PaddlePaddle复现论文：[Longformer: The Long-Document Transformer](https://arxiv.org/pdf/2004.05150.pdf)

## Longformer
[The Long-Document Transformer](https://arxiv.org/pdf/2004.05150.pdf)

Longformer提出局部窗口注意力与任务驱动的全局注意力机制相结合的方式，取代原有O(n2)的标准注意力机制，来解决模型无法处理长文本的问题。
Longformer模型是基于RoBERTa模型的改进，在对Longformer进行预训练和下游任务微调后，在WikiHop和TriviaQA数据集上相比RoBERTa取得了SOTA结果。

### 1. Tokenizer

参考pytorch：https://github.com/huggingface/transformers/blob/main/src/transformers/models/roberta/tokenization_roberta.py

参考paddle：https://github.com/PaddlePaddle/PaddleNLP/blob/develop/paddlenlp/transformers/bigbird/tokenizer.py

### 2. Modeling

参考pytorch：https://github.com/huggingface/transformers/blob/main/src/transformers/models/longformer/modeling_longformer.py

### 3. Attention
https://github.com/PaddlePaddle/PaddleNLP/blob/develop/paddlenlp/transformers/attention_utils.py

### 4. 预训练模型权重转换

模格式转换教程：https://paddlenlp.readthedocs.io/zh/latest/community/contribute_models/convert_pytorch_to_paddle.html

### 5. 下游任务精度验证

数据集：Wiki-Hop，TriviaQA，arXiv 三个数据集任务结果复现

验收标准：
1. longformer-large-4096 模型在 Wiki-Hop 验证集上 Acc=81.9, 在 TriviaQA 验证集上 F1=77.3 (见论文 Table-8)
2. led-large-16384 模型在 arXiv-summarization 验证集上 R-1=46.63, R-2=19.62, R-L=41.83 (见论文 Table-9)
