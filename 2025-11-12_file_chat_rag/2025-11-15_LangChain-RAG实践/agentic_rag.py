# pip install Pillow
# pip install -qU langchain-milvus
import os

# 1、解析并加载文档
from langchain_community.document_loaders.parsers import LLMImageBlobParser
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_milvus import Milvus
from langchain_openai import ChatOpenAI
from langchain_pymupdf4llm import PyMuPDF4LLMLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode, tools_condition


def extract_pdf_text_with_images(pdf_file: str) -> list:
    """
    提取pdf中的文本信息，如果包含图片，也同步解析成文本
    :param pdf_file:
    :return:
    """
    _PROMPT_IMAGES_TO_DESCRIPTION: str = (
        "您是一名负责为图像检索任务生成摘要的助手。"
        "1. 这些摘要将被嵌入并用于检索原始图像。"
        "请提供简洁的图像摘要，确保其高度优化以利于检索\n"
        "2. 提取图像中的所有文本内容。"
        "不得遗漏页面上的任何信息。\n"
        "3. 不要凭空捏造不存在的信息\n"
        "请使用Markdown格式直接输出答案，"
        "无需解释性文字，且开头不要使用Markdown分隔符```。"
    )

    llm_parser = LLMImageBlobParser(
        model=ChatOpenAI(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key="fb15035a-4d78-4f40-b139-a07743ce84a3",
            model="doubao-seed-1-6-vision-250815",
            max_tokens=8192
        ),
        prompt=_PROMPT_IMAGES_TO_DESCRIPTION
    )

    loader = PyMuPDF4LLMLoader(
        pdf_file,
        mode="single",  # 作为单个文档处理
        extract_images=True,  # 提取图片
        table_strategy="lines",  # 提取表格
        images_parser=llm_parser
    )
    documents = loader.load()
    print(documents)
    return documents


def spill_pdf_text(documents) -> list:
    """
    将PDF文件拆分为多个小文件，每个小文件包含一个页面的内容
    :param documents:
    :return:
    """

    # docs_list = [Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='这次的行程主要是以菩提迦耶为起点去参加活动，然后再在北 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 走走，15 天左右，\n\n\n出发前并没有具体的行程安排，主打一个随性风，行李也是能少带就少带，尽量到当地\n\n\n购买。\n\n\n[15 天的行程，安排的还是毕竟宽裕的，前往了菩提迦耶-瓦拉纳希- 阿格拉](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/18034.html) [- 新德里](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/16120.html)\n\n\n\n![### 图像摘要  \n机场停机坪场景，**泰国亚航（THAI AIRASIA）**的空客（AIRBUS）飞机（红白涂装，机身印 `airasia.com`、发动机/尾翼印 `AirAsia`），乘客排队经登机梯登机；背景为蓝天、机场灯杆、地勤车辆。  \n\n\n### 提取的文本  \n- 飞机机身：`airasia.com`  \n- 机头区域：`THAI AIRASIA`、`AIRBUS`  \n- 发动机/尾翼：`AirAsia`](#)\n\n-----\n\n# 出发前：\n\n1）关于水源：翻看了很多的游记，都说去 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 一定要特别注意水源，甚至有建议拿\n\n\n瓶装水刷牙漱口的情况，但是这 15 天下来我的看法是没必要。除了平日里喝的水我会\n\n\n用瓶装水，其他的时候都是使用水龙头的水源，也在路边摊吃过，喝了无数杯 Masala tea\n\n\n/ Honey lemon tea 也都没事，不知道是不是近几年来 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 进步了，还是我的免疫力最\n\n\n近比较强大，总而言之，心态重要，既然选择去 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 旅行心态就得放平。\n\n\n2）一定需要准备的物品：\n\n\n1. 合适的转换头合适的转换头合适的转换头。什么叫做合适，就是建议去买适合 [印](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html)\n\n\n[度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 的欧标，一定要粗款圆头的，并不是表明欧标标准的就可以使用，圆头也有分小圆\n\n\n[头和大圆头，我买了一个多合一的转接头，结果圆头太小，很多时候接触时长不良，造](https://www.mafengwo.cn/photo/10182/scenery_24573398/1908756401.html)\n\n\n成不便。关键词： [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 转换插头。\n\n\n2. 柔软舒适又宽大围巾。女生如果是独自出行的话（就算不是独自出行）我觉得低调\n\n\n一些的用围巾把自己包裹起来，也是保护自己安全的选择。如果不需要包裹起来，在 1\n\n\n月份的北 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) ，保暖和用来遮挡住难闻气味也非常实用。在北 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 很容易就鼻孔内全\n\n\n部黑掉，空气质量差。\n\n\n3. 保温杯。有时候餐厅里的水会肉眼的感觉浑浊，自己带上保温杯在酒店里装好水，\n\n\n带出去喝。\n\n\n4. 吹风机。RMB200-350 的酒店很多也没有吹风机，和国内不太一样，建议提前准备\n\n\n好。\n\n\n3）简单的药品：感冒药，降火药，肠胃药。\n\n\n其他药我都带了，但是这次没带上降火的药是我的一大失算，因为 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 的饮食口味偏\n\n\n重，又咸又辣又爱放各式的香料。在我们老中医里，有些香料是会导致人上火的， [比](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/63538.html)\n\n\n[如](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/63538.html) 说「肉桂」。平日里吃清淡的人去那边就肯定多少招罪，我没吃两天就感觉到自己\n\n\n口干舌燥，肺部及其燥热，而且北 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 的空气质量及其糟糕，雾霾很重，肺部不太好\n\n\n的朋友更是要准备好常备药。肠胃药倒是从未使用上，但还是得有备无患吧，毕竟 [印](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html)\n\n\n\n-----\n\n[度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 口音还是有点难听懂，闹肚子买错药就麻烦了，我带的是 [日本](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10183.html) 喇叭牌，很好用。感\n\n\n冒药是带的 999 感冒灵颗粒，有备无患，结果全部喝光，1 月的北 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 还是会冷的，\n\n\n温差大。\n\n\n4）礼品类：在 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 有朋友的话可以带上 [中国](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/21536.html) 的茶叶，例如 [云南普洱](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/12711.html) 茶， [杭州](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10156.html) 西\n\n\n湖 [龙井](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/64861.html) 茶等，那边的朋友会很喜欢。（或是一些具有 [中国](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/21536.html) 传统文化气息的物品）\n\n\n5）电子设备类：我带了 Sony A7c 相机 / 2 颗镜头 28-200 & 55 1.8 / 电脑 / 鼠标 / 硬\n\n\n盘 / 3 张 128G 的卡 / 充电线们 / 脚架\n\n\n6）衣物类：轻薄保暖的衣物，薄款羽绒服，一次性袜子，一次性内裤。1 月的北印我\n\n\n的穿搭公式基本是以保暖内衣+薄的内搭 1 件+薄的外套或者上衣+薄的长款羽绒服为主。\n\n\n这样穿天气热的时候脱掉羽绒服也刚好，冷的时候长款羽绒服也巨挡风，很完美。裤子\n\n\n一般是保暖裤+长筒袜，道理一样，热的时候长筒袜往低处放，透气性就出来了。\n\n\n7）把来回行程单和签证单打印出来，帮助你在没有网路，和找不到打印店的时候，省\n\n\n下很多麻烦（过海关，登机时都会用到）我还打印了身份证/护照，以防丢失了证件，\n\n\n他们就会起到很大的帮助。\n\n\n8）通讯：我是提前在某宝上买了 15 天的 [Sim 卡，信号一般，有总比没有强，有伙伴](https://www.mafengwo.cn/photo/10182/scenery_24573398/1911674452.html)\n\n\n推荐在飞机场买，但是因为我去的是小机场，所以还是提前买了， [新德里](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/16120.html) 的话到当地\n\n\n买应该也没问题。\n\n\n9）必下 App：住宿用「Boking」线上预约，可到酒店后用现金支付\n\n\n找景点和体验用「tripadvisor」最值得去的景点，和当地的文化体验在上面能找到，就\n\n\n是信号总是很差有时候打不开，我会转用谷歌地图\n\n\n叫车用「Uber」小轿车/Tutu 三轮车都可以在上面叫，也可以用上面的价格比价，避免\n\n\n被司机坑\n\n\n地图用「Google」基本上信息还是很全面的，想去哪里都可以搜索，信息更新的也比\n\n\n价及时\n\n\n10）现金：提前到银行换美金，再到当地换卢比。\n\n\n\n-----\n\n![### 图像摘要  \n一只手扇状持握多份印度储备银行（RESERVE BANK OF INDIA）500卢比（₹500）纸币，纸币印甘地（MAHATMA GANDHI）头像、印地语/英语文字、序列号（如4VK128805、6EB594850等）；背景含深色皮革物品、蓝/黑/白色衣物。  \n\n\n### 提取的文本内容  \n#### 印地语  \n-  भारतीय रिज़र्व बैंक  \n-  पांच सौ रुपये  \n-  केंद्र सरकार द्वारा सुनिश्चित किया जाता है  \n\n\n#### 英语  \n-  RESERVE BANK OF INDIA  \n-  GUARANTEED BY THE CENTRAL GOVERNMENT  \n-  I PROMISE TO PAY THE BEARER THE SUM OF FIVE HUNDRED RUPEES  \n-  MAHATMA GANDHI  \n\n\n#### 符号与序列号  \n-  ₹500  \n-  序列号：4VK128805、6EB594850、AH 855123、28805  \n\n\n（注：文本提取基于图像可见区域，部分被遮挡文字保留核心可辨识内容。）](#)\n# 希望这几个点能对你有帮助：\n\n1. 买东西前提前问好价格 2. 夜晚尽量避免出门 3.把包包看好，我是习惯多背一个小\n\n\n小包，专门来放证件和现金，从不离身。 4. 女生把自己包裹严实，外套为黑灰低调色，\n\n\n内搭随意靓丽。\n\n\n\n-----\n\n在 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 很容易被人问合照，看自己的意愿吧，一旦接受了拍照就有点难以停下来，会\n\n\n有很多人想找你拍\n\n\n在这段时间里，我遇过跟最初说的价格不一样，在极限拉扯的司机，也遇到过看我们在\n\n\n夜路上行走不便，顺道载我们一程的司机。有看我们是 [亚洲](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/52314.html) 面孔就提高售卖价格的商\n\n\n贩，也有在一旁挥挥手暗示我们这个售价过高的 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 人。有不怀好意盯着你的人群，\n\n\n也有满怀笑意给我两颗糖的小女孩。\n\n\n我认为，保护好自身安全，是第一要义。但是若太过于把自己放在一个“受害“角色上的\n\n\n行程，也是不可取的。毕竟， [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 不是一个能让人好好放松和享受的地方，它带来的\n\n\n氛围更多的是喧闹、吵杂、无常变化。这是目前为止我走过的最为不在常态化行程里进\n\n\n行的旅程。\n\n\n\n-----\n\n![### 图像摘要  \n一群人（含戴墨镜、围巾的女士及印度当地民众）在印度古迹（大型石塔建筑）前合影，背景有树木、绿植；图中文字标注印度游学Vlog行程：**菩提迦耶-瓦拉纳希-阿格拉-新德里**，时间**2023.12.27-2024.01.10**。  \n\n\n### 提取文本  \n「印度游学Vlog」  \n菩提迦耶-瓦拉纳希-阿格拉-新德里  \n2023.12.27-2024.01.10](#)\n')]

    # text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=50, separators=["\n\n", "\n", "。", ""])
    # texts = text_splitter.split_text(document)

    # markdown格式解析
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1024, chunk_overlap=200
    )
    doc_splits = text_splitter.split_documents(documents)
    print(doc_splits)
    return doc_splits
# docs = [Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='这次的行程主要是以菩提迦耶为起点去参加活动，然后再在北 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 走走，15 天左右，'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='出发前并没有具体的行程安排，主打一个随性风，行李也是能少带就少带，尽量到当地\n\n\n购买。'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[15 天的行程，安排的还是毕竟宽裕的，前往了菩提迦耶-瓦拉纳希-'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='阿格拉](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/18034.html) [- 新德里](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/16120.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='![### 图像摘要'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='机场停机坪场景，**泰国亚航（THAI AIRASIA）**的空客（AIRBUS）飞机（红白涂装，机身印'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='AIRASIA）**的空客（AIRBUS）飞机（红白涂装，机身印 `airasia.com`、发动机/尾翼印'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='`airasia.com`、发动机/尾翼印 `AirAsia`），乘客排队经登机梯登机；背景为蓝天、机场灯杆、地勤车辆。'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='### 提取的文本  \n- 飞机机身：`airasia.com`  \n- 机头区域：`THAI AIRASIA`、`AIRBUS`  \n- 发动机/尾翼：`AirAsia`](#)\n\n-----'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='-----\n\n# 出发前：'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='1）关于水源：翻看了很多的游记，都说去 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 一定要特别注意水源，甚至有建议拿'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='瓶装水刷牙漱口的情况，但是这 15 天下来我的看法是没必要。除了平日里喝的水我会'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='用瓶装水，其他的时候都是使用水龙头的水源，也在路边摊吃过，喝了无数杯 Masala tea'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='/ Honey lemon tea 也都没事，不知道是不是近几年来 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 进步了，还是我的免疫力最'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='近比较强大，总而言之，心态重要，既然选择去 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 旅行心态就得放平。'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='2）一定需要准备的物品：'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='1. 合适的转换头合适的转换头合适的转换头。什么叫做合适，就是建议去买适合'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[印](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='的欧标，一定要粗款圆头的，并不是表明欧标标准的就可以使用，圆头也有分小圆'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[头和大圆头，我买了一个多合一的转接头，结果圆头太小，很多时候接触时长不良，造](https://www'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='太小，很多时候接触时长不良，造](https://www.mafengwo.cn/photo/10182/scenery_24573398/190875640'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='mafengwo.cn/photo/10182/scenery_24573398/1908756401.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='成不便。关键词： [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 转换插头。'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='2. 柔软舒适又宽大围巾。女生如果是独自出行的话（就算不是独自出行）我觉得低调'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='一些的用围巾把自己包裹起来，也是保护自己安全的选择。如果不需要包裹起来，在 1'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='月份的北 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) ，保暖和用来遮挡住难闻气味也非常实用。在北'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='，保暖和用来遮挡住难闻气味也非常实用。在北 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 很容易就鼻孔内全'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='部黑掉，空气质量差。'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='3. 保温杯。有时候餐厅里的水会肉眼的感觉浑浊，自己带上保温杯在酒店里装好水，\n\n\n带出去喝。'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='带出去喝。\n\n\n4. 吹风机。RMB200-350 的酒店很多也没有吹风机，和国内不太一样，建议提前准备\n\n\n好。'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='好。\n\n\n3）简单的药品：感冒药，降火药，肠胃药。'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='其他药我都带了，但是这次没带上降火的药是我的一大失算，因为 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 的饮食口味偏'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='重，又咸又辣又爱放各式的香料。在我们老中医里，有些香料是会导致人上火的，'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[比](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/63538.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[如](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/63538.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='说「肉桂」。平日里吃清淡的人去那边就肯定多少招罪，我没吃两天就感觉到自己'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='口干舌燥，肺部及其燥热，而且北 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 的空气质量及其糟糕，雾霾很重，肺部不太好'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='的朋友更是要准备好常备药。肠胃药倒是从未使用上，但还是得有备无患吧，毕竟'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[印](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='-----'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 口音还是有点难听懂，闹肚子买错药就麻烦了，我带的是'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[日本](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10183.html) 喇叭牌，很好用。感'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='冒药是带的 999 感冒灵颗粒，有备无患，结果全部喝光，1 月的北 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='月的北 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 还是会冷的，'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='温差大。'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='4）礼品类：在 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 有朋友的话可以带上'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 有朋友的话可以带上 [中国](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/21536.html) 的茶叶，例如'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[中国](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/21536.html) 的茶叶，例如 [云南普洱](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/12711.html) 茶，'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[云南普洱](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/12711.html) 茶， [杭州](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10156.html) 西'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='湖 [龙井](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/64861.html) 茶等，那边的朋友会很喜欢。（或是一些具有'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='茶等，那边的朋友会很喜欢。（或是一些具有 [中国](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/21536.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[中国](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/21536.html) 传统文化气息的物品）'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='5）电子设备类：我带了 Sony A7c 相机 / 2 颗镜头 28-200 & 55 1.8 / 电脑 / 鼠标 / 硬'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='盘 / 3 张 128G 的卡 / 充电线们 / 脚架'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='6）衣物类：轻薄保暖的衣物，薄款羽绒服，一次性袜子，一次性内裤。1 月的北印我'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='的穿搭公式基本是以保暖内衣+薄的内搭 1 件+薄的外套或者上衣+薄的长款羽绒服为主。'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='这样穿天气热的时候脱掉羽绒服也刚好，冷的时候长款羽绒服也巨挡风，很完美。裤子'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='一般是保暖裤+长筒袜，道理一样，热的时候长筒袜往低处放，透气性就出来了。'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='7）把来回行程单和签证单打印出来，帮助你在没有网路，和找不到打印店的时候，省'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='下很多麻烦（过海关，登机时都会用到）我还打印了身份证/护照，以防丢失了证件，'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='他们就会起到很大的帮助。'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='8）通讯：我是提前在某宝上买了 15 天的 [Sim'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='15 天的 [Sim 卡，信号一般，有总比没有强，有伙伴](https://www.mafengwo.cn/photo/10182/scenery_24573398/1911674452.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='推荐在飞机场买，但是因为我去的是小机场，所以还是提前买了， [新德里](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/16120.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[新德里](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/16120.html) 的话到当地'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='买应该也没问题。\n\n\n9）必下 App：住宿用「Boking」线上预约，可到酒店后用现金支付'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='找景点和体验用「tripadvisor」最值得去的景点，和当地的文化体验在上面能找到，就'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='是信号总是很差有时候打不开，我会转用谷歌地图'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='叫车用「Uber」小轿车/Tutu 三轮车都可以在上面叫，也可以用上面的价格比价，避免\n\n\n被司机坑'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='被司机坑\n\n\n地图用「Google」基本上信息还是很全面的，想去哪里都可以搜索，信息更新的也比\n\n\n价及时'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='价及时\n\n\n10）现金：提前到银行换美金，再到当地换卢比。\n\n\n\n-----'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='![### 图像摘要'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='一只手扇状持握多份印度储备银行（RESERVE BANK OF INDIA）500卢比（₹500）纸币，纸币印甘地（MAHATMA'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='GANDHI）头像、印地语/英语文字、序列号（如4VK128805、6EB594850等）；背景含深色皮革物品、蓝/'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='805、6EB594850等）；背景含深色皮革物品、蓝/黑/白色衣物。'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='### 提取的文本内容  \n#### 印地语  \n-  भारतीय रिज़र्व बैंक  \n-  पांच सौ रुपये'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='-  पांच सौ रुपये  \n-  केंद्र सरकार द्वारा सुनिश्चित किया जाता है'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='#### 英语  \n-  RESERVE BANK OF INDIA  \n-  GUARANTEED BY THE CENTRAL GOVERNMENT  \n-  I PROMISE TO PAY THE BEARER THE SUM OF FIVE HUNDRED RUPEES  \n-  MAHATMA GANDHI'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='#### 符号与序列号  \n-  ₹500  \n-  序列号：4VK128805、6EB594850、AH 855123、28805'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='（注：文本提取基于图像可见区域，部分被遮挡文字保留核心可辨识内容。）](#)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='# 希望这几个点能对你有帮助：'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='1. 买东西前提前问好价格 2. 夜晚尽量避免出门 3.把包包看好，我是习惯多背一个小'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='小包，专门来放证件和现金，从不离身。 4. 女生把自己包裹严实，外套为黑灰低调色，'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='内搭随意靓丽。\n\n\n\n-----'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='在 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='很容易被人问合照，看自己的意愿吧，一旦接受了拍照就有点难以停下来，会'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='有很多人想找你拍\n\n\n在这段时间里，我遇过跟最初说的价格不一样，在极限拉扯的司机，也遇到过看我们在'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='夜路上行走不便，顺道载我们一程的司机。有看我们是 [亚洲](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/52314.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[亚洲](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/52314.html) 面孔就提高售卖价格的商'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='贩，也有在一旁挥挥手暗示我们这个售价过高的 [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 人。有不怀好意盯着你的人群，'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='也有满怀笑意给我两颗糖的小女孩。'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='我认为，保护好自身安全，是第一要义。但是若太过于把自己放在一个“受害“角色上的'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='行程，也是不可取的。毕竟， [印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html)'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='[印度](https://www.mafengwo.cn/travel-scenic-spot/mafengwo/10182.html) 不是一个能让人好好放松和享受的地方，它带来的'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='氛围更多的是喧闹、吵杂、无常变化。这是目前为止我走过的最为不在常态化行程里进\n\n\n行的旅程。\n\n\n\n-----'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='![### 图像摘要'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='一群人（含戴墨镜、围巾的女士及印度当地民众）在印度古迹（大型石塔建筑）前合影，背景有树木、绿'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='古迹（大型石塔建筑）前合影，背景有树木、绿植；图中文字标注印度游学Vlog行程：**菩提迦耶'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='植；图中文字标注印度游学Vlog行程：**菩提迦耶-瓦拉纳希-阿格拉-新德里**，时间**2023.12.27-'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='-瓦拉纳希-阿格拉-新德里**，时间**2023.12.27-2024.01.10**。'), Document(metadata={'producer': '', 'creator': 'WPS 文字', 'creationdate': '2024-11-20T22:31:19+08:00', 'source': '旅行日记.pdf', 'file_path': '旅行日记.pdf', 'total_pages': 6, 'format': 'PDF 1.7', 'title': '', 'author': '田威峰', 'subject': '', 'keywords': '', 'moddate': '2024-11-20T22:31:19+08:00', 'trapped': '', 'modDate': "D:20241120223119+08'00'", 'creationDate': "D:20241120223119+08'00'"}, page_content='### 提取文本  \n「印度游学Vlog」  \n菩提迦耶-瓦拉纳希-阿格拉-新德里  \n2023.12.27-2024.01.10](#)')]


def embedding_text_into_vector_store(doc_splits):
    from langchain_core.vectorstores import InMemoryVectorStore

    from langchain_ollama import OllamaEmbeddings

    embedding = OllamaEmbeddings(
        model="qwen3-embedding:0.6b",
        base_url="http://35.235.113.151:11434",
        temperature=0
    )

    from langchain_milvus import Milvus

    URI = "http://207.246.94.177:19530"
    # 将texts转换为向量，并保存在向量数据库中
    vector_store = Milvus.from_documents(doc_splits,
                                         embedding=embedding,
                                         collection_name="langchainweb",
                                         connection_args={"uri": URI})

    # vector_store = Milvus(
    #     embedding_function=embedding,
    #     connection_args={"uri": URI},
    #     index_params={"index_type": "FLAT", "metric_type": "L2"},
    # )

    # 将文本信息转换为向量存储
    # vector_store = InMemoryVectorStore.from_documents(
    #     documents=docs, embedding=embedding
    # )
    # s = vectorstore.search("去哪里旅行了",search_type="similarity")
    # print(s)
    return vector_store

def add_document_to_vectorstore():
    pdf_file = "../llm_course.pdf"
    documents = extract_pdf_text_with_images(pdf_file)
    vector_store = embedding_text_into_vector_store(documents)

# -------------------------以上代码完成文档入库---------------------
def create_retriever_tool(vectorstore: VectorStore):
    from langchain_classic.tools.retriever import create_retriever_tool
    # “VectorStoreRetriever
    # 支持 “相似性”（默认）、“mmr”（最大边际相关性，上文已描述）和 “相似性分数阈值” 这几种搜索类型。我们可以使用最后一种类型，根据相似性分数对检索器输出的文档进行阈值筛选。检索器可以轻松地集成到更复杂的应用程序中，例如检索增强型生成（RAG）应用程序，它将给定的问题与检索到的上下文结合起来，为
    # LLM
    # 构造提示。
    #
    # ### 解释说明
    # - ** VectorStoreRetriever
    # 支持的搜索类型 **：
    # - ** 相似性（similarity） ** ：这是默认的搜索类型，它会根据文档与查询之间的相似性来检索文档。相似性通常是通过计算文档向量和查询向量之间的距离（如余弦相似度）来衡量的。
    # - ** 最大边际相关性（mmr，maximum
    # marginal
    # relevance） ** ：这种搜索类型旨在平衡检索结果的相似性和多样性。它不仅考虑文档与查询的相似性，还会考虑文档之间的差异性，以避免检索到过于相似的文档，从而提高检索结果的多样性。
    # - ** 相似性分数阈值（similarity_score_threshold） ** ：这种搜索类型允许用户设置一个相似性分数的阈值，只有当文档的相似性分数高于这个阈值时，才会被检索出来。这可以用于过滤掉与查询相关性较低的文档，提高检索结果的质量。
    # - ** 检索器的应用 **：
    # - 检索器可以集成到更复杂的应用程序中，例如检索增强型生成（RAG）应用程序。

    retriever = vectorstore.as_retriever()

    retriever_tool = create_retriever_tool(
        retriever,
        "retrieve_document",
        "搜索并返回旅行的相关信息",
    )
    # retriever_tool.invoke({"query": "他们乘坐什么航班去旅行了"})
    return retriever_tool
def retrieve_tool():
    from langchain_ollama import OllamaEmbeddings

    embedding = OllamaEmbeddings(
        model="qwen3-embedding:0.6b",
        base_url="http://35.235.113.151:11434",
        temperature=0
    )
    URI = "http://207.246.94.177:19530"
    vector_store = Milvus(
        embedding_function=embedding,
        connection_args={"uri": URI},
        index_params={"index_type": "FLAT", "metric_type": "L2"},
    )
    return create_retriever_tool(vector_store)

# -----------------------------------------------------------------------


def get_deepseek_model():
    os.environ["DEEPSEEK_API_KEY"] = "sk-3b351274b99e41679b0c014ae1f6096a"
    model = init_chat_model("deepseek:deepseek-chat", temperature=0)
    return model


# ===== 提示词模板 =====

GRADE_PROMPT = (
    "你是一个文档相关性评估专家，负责评估检索到的文档与用户问题的相关性。\n\n"
    "【检索到的文档】：\n{context}\n\n"
    "【用户问题】：\n{question}\n\n"
    "【评估标准】：\n"
    "- 如果文档包含与用户问题相关的关键词、概念或语义信息，则判定为相关\n"
    "- 如果文档内容能够帮助回答用户问题，则判定为相关\n"
    "- 如果文档与问题完全无关或信息不足，则判定为不相关\n\n"
    "【输出要求】：\n"
    "请给出二元评分：'yes'（相关）或 'no'（不相关）"
)

REWRITE_PROMPT = (
    "你是一个问题优化专家，擅长理解用户问题的深层语义意图并重新表述问题。\n\n"
    "【原始问题】：\n"
    "-------------------\n"
    "{question}\n"
    "-------------------\n\n"
    "【任务要求】：\n"
    "1. 分析问题的核心语义和潜在意图\n"
    "2. 识别问题中的关键概念和隐含需求\n"
    "3. 将问题重新表述得更加清晰、具体和易于检索\n"
    "4. 保持原问题的核心意图不变\n\n"
    "【优化后的问题】："
)

GENERATE_PROMPT = (
    "你是一个专业的问答助手，擅长基于检索到的上下文信息回答用户问题。\n\n"
    "【用户问题】：\n{question}\n\n"
    "【检索到的上下文】：\n{context}\n\n"
    "【回答要求】：\n"
    "1. 仔细阅读上下文信息，基于事实进行回答\n"
    "2. 如果上下文中包含答案，请准确提取并组织成连贯的回答\n"
    '3. 如果上下文信息不足以回答问题，请明确说明"根据现有信息无法回答"\n'
    "4. 回答要简洁明了，控制在3-5句话以内\n"
    "5. 使用专业、友好的语气\n"
    "6. 不要编造或推测上下文中没有的信息\n\n"
    "【你的回答】："
)


class AgenticRAGEngine:
    """Agentic RAG 引擎"""

    def __init__(self,
                 knowledge_base: str = None,
                 vector_service=None,
                 milvus_service=None):
        self.knowledge_base = knowledge_base or settings.DEFAULT_KNOWLEDGE_BASE
        self.vector_service = vector_service
        self.milvus_service = milvus_service
        self.retriever = None
        self.retriever_tool = None
        self.response_model = None
        self.grader_model = None
        self.graph = None
        self.file_processor = None
        self._initialized = False

    async def initialize(self):
        """初始化引擎"""
        if self._initialized:
            return

        try:
            # 初始化向量服务
            if self.vector_service is None:
                self.vector_service = await VectorServiceFactory.get_default_service()

            # 初始化Milvus服务
            if self.milvus_service is None:
                self.milvus_service = await MilvusServiceFactory.create_service(
                    knowledge_base=self.knowledge_base,
                    dimension=self.vector_service.dimension
                )

            # 创建检索器

            # 创建检索工具
            if create_retriever_tool is not None:
                self.retriever_tool = create_retriever_tool(
                    self.retriever,
                    "retrieve_documents",
                    f"Search and return information from {self.knowledge_base} knowledge base."
                )

            # 初始化LLM模型
            if init_chat_model is not None:
                self.response_model = init_chat_model(
                    f"deepseek:{settings.LLM_MODEL}",
                    temperature=settings.LLM_TEMPERATURE,
                    max_tokens=settings.LLM_MAX_TOKENS,
                    api_key=settings.LLM_API_KEY,
                    base_url=settings.LLM_API_BASE
                )
                self.grader_model = self.response_model

            # 构建图
            if StateGraph is not None:
                await self._build_graph()

            self._initialized = True
            logger.info(f"Agentic RAG engine initialized for knowledge base: {self.knowledge_base}")

        except Exception as e:
            logger.error(f"Failed to initialize Agentic RAG engine: {str(e)}")
            raise

    async def _build_graph(self):
        """构建LangGraph工作流"""
        workflow = StateGraph(MessagesState)

        # 添加节点
        workflow.add_node("generate_query_or_respond", self._generate_query_or_respond)
        workflow.add_node("retrieve", ToolNode([self.retriever_tool]))
        workflow.add_node("grade_documents", self._grade_documents)
        workflow.add_node("rewrite_question", self._rewrite_question)
        workflow.add_node("generate_answer", self._generate_answer)

        # 添加边
        workflow.add_edge(START, "generate_query_or_respond")

        # 决定是否检索
        workflow.add_conditional_edges(
            "generate_query_or_respond",
            tools_condition,
            {
                "tools": "retrieve",
                END: END,
            },
        )

        # 检索后的条件边
        workflow.add_conditional_edges(
            "retrieve",
            self._grade_documents,
        )

        workflow.add_edge("generate_answer", END)
        workflow.add_edge("rewrite_question", "generate_query_or_respond")

        # 编译图
        self.graph = workflow.compile()

    def _generate_query_or_respond(self, state):
        """生成查询或直接回答"""
        if self.response_model is None:
            return {"messages": [{"role": "assistant", "content": "LLM model not available"}]}

        try:
            response = (
                self.response_model
                .bind_tools([self.retriever_tool])
                .invoke(state["messages"])
            )
            return {"messages": [response]}
        except Exception as e:
            return {"messages": [{"role": "assistant", "content": f"Error: {str(e)}"}]}

    def _grade_documents(self, state) -> Literal["generate_answer", "rewrite_question"]:
        """评估检索文档的相关性"""
        if not settings.RAG_ENABLE_GRADING:
            return "generate_answer"

        if self.grader_model is None:
            return "generate_answer"

        try:
            question = state["messages"][0].content
            context = state["messages"][-1].content

            prompt = GRADE_PROMPT.format(question=question, context=context)
            response = (
                self.grader_model
                .with_structured_output(GradeDocuments)
                .invoke([{"role": "user", "content": prompt}])
            )

            score = response.binary_score
            if score == "yes":
                return "generate_answer"
            else:
                # 检查迭代次数
                iteration_count = getattr(state, 'iteration_count', 0)
                if iteration_count >= settings.RAG_MAX_ITERATIONS:
                    return "generate_answer"
                return "rewrite_question"

        except Exception as e:
            logger.error(f"Error in grade_documents: {str(e)}")
            return "generate_answer"

    def _rewrite_question(self, state):
        """重写问题"""
        if not settings.RAG_ENABLE_REWRITE:
            return {"messages": state["messages"]}

        if self.response_model is None:
            return {"messages": state["messages"]}

        try:
            messages = state["messages"]
            question = messages[0].content
            prompt = REWRITE_PROMPT.format(question=question)
            response = self.response_model.invoke([{"role": "user", "content": prompt}])

            # 增加迭代计数
            iteration_count = getattr(state, 'iteration_count', 0) + 1

            return {
                "messages": [{"role": "user", "content": response.content}],
                "iteration_count": iteration_count
            }
        except Exception as e:
            logger.error(f"Error in rewrite_question: {str(e)}")
            return {"messages": state["messages"]}

    def _generate_answer(self, state):
        """生成最终答案"""
        if self.response_model is None:
            return {"messages": [{"role": "assistant", "content": "LLM model not available"}]}

        try:
            question = state["messages"][0].content
            context = state["messages"][-1].content
            prompt = GENERATE_PROMPT.format(question=question, context=context)
            response = self.response_model.invoke([{"role": "user", "content": prompt}])
            return {"messages": [response]}
        except Exception as e:
            logger.error(f"Error in generate_answer: {str(e)}")
            return {"messages": [{"role": "assistant", "content": f"Error generating answer: {str(e)}"}]}


class AgenticRAGEngineFactory:
    """Agentic RAG引擎工厂类"""

    _instances = {}

    @classmethod
    async def create_engine(cls, knowledge_base: str = None) -> AgenticRAGEngine:
        """创建或获取引擎实例"""
        knowledge_base = knowledge_base or settings.DEFAULT_KNOWLEDGE_BASE

        if knowledge_base not in cls._instances:
            engine = AgenticRAGEngine(knowledge_base=knowledge_base)
            await engine.initialize()
            cls._instances[knowledge_base] = engine
            logger.info(f"Created new Agentic RAG engine for knowledge base: {knowledge_base}")

        return cls._instances[knowledge_base]

    @classmethod
    async def get_default_engine(cls) -> AgenticRAGEngine:
        """获取默认引擎"""
        return await cls.create_engine()

    @classmethod
    def clear_instances(cls):
        """清理所有实例"""
        cls._instances.clear()
        logger.info("Cleared all Agentic RAG engine instances")
