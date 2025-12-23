

教程：

 https://ollama.com/library/qwen3-embedding:0.6b


ollama (容器安装)

/data/ollama

服务器访问：[http://54.179.103.192:11434/api/tags](http://127.0.0.1:11434/api/tags)

远程访问：

[http://54.179.103.192:11434/api/tags](http://54.179.103.192:11434/api/tags)



text="""

你好

""

fromlangchain_ollamaimportOllamaEmbeddings

# pip install -qU langchain-ollama

# https://docs.langchain.com/oss/python/integrations/text_embedding/ollama

embeddings=OllamaEmbeddings(

model="qwen3-embedding:0.6b",

base_url="http://54.179.103.192:11434/"

)

s=embeddings.embed_query(text)

print(s)
