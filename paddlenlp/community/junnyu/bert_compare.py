import paddle
import paddlenlp.transformers as ppnlp

import torch
import transformers as hgnlp


def compare_math():
    text = "students apply these new understandings as they reason about and perform decimal [MASK] through the hundredths place."
    # ppnlp
    path = "junnyu/tbs17-MathBERT"
    model = ppnlp.BertForPretraining.from_pretrained(path)
    tokenizer = ppnlp.BertTokenizer.from_pretrained(path)
    model.eval()
    text = "students apply these new understandings as they reason about and perform decimal [MASK] through the hundredths place."
    tokens = ["[CLS]"]
    text_list = text.split("[MASK]")
    for i, t in enumerate(text_list):
        tokens.extend(tokenizer.tokenize(t))
        if i == len(text_list) - 1:
            tokens.extend(["[SEP]"])
        else:
            tokens.extend(["[MASK]"])

    input_ids_list = tokenizer.convert_tokens_to_ids(tokens)
    input_ids = paddle.to_tensor([input_ids_list])
    with paddle.no_grad():
        pd_outputs = model(input_ids)[0][0]
    pd_outputs_sentence = "paddle: "
    for i, id in enumerate(input_ids_list):
        if id == tokenizer.convert_tokens_to_ids(["[MASK]"])[0]:
            scores, index = paddle.nn.functional.softmax(pd_outputs[i],
                                                         -1).topk(5)
            tokens = tokenizer.convert_ids_to_tokens(index.tolist())
            outputs = []
            for score, tk in zip(scores.tolist(), tokens):
                outputs.append(f"{tk}={score}")
            pd_outputs_sentence += "[" + "||".join(outputs) + "]" + " "
        else:
            pd_outputs_sentence += "".join(
                tokenizer.convert_ids_to_tokens(
                    [id], skip_special_tokens=True)) + " "

    print(pd_outputs_sentence)

    #paddle:  students apply these new understanding ##s as they reason about and perform decimal [numbers=0.8327996134757996||##s=0.0865364819765091||operations=0.0313422717154026||placement=0.019931407645344734||places=0.01254698634147644] through the hundred ##ths place . 

    # transformers
    path = "tbs17/MathBERT"
    model = hgnlp.BertForPreTraining.from_pretrained(path)
    tokenizer = hgnlp.BertTokenizer.from_pretrained(path)
    model.eval()

    inputs = tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        pt_outputs = model(**inputs).prediction_logits[0]
    pt_outputs_sentence = "pytorch: "
    for i, id in enumerate(inputs["input_ids"][0].tolist()):
        if id == tokenizer.convert_tokens_to_ids(["[MASK]"])[0]:
            scores, index = torch.nn.functional.softmax(pt_outputs[i],
                                                        -1).topk(5)
            tokens = tokenizer.convert_ids_to_tokens(index.tolist())
            outputs = []
            for score, tk in zip(scores.tolist(), tokens):
                outputs.append(f"{tk}={score}")
            pt_outputs_sentence += "[" + "||".join(outputs) + "]" + " "
        else:
            pt_outputs_sentence += "".join(
                tokenizer.convert_ids_to_tokens(
                    [id], skip_special_tokens=True)) + " "

    print(pt_outputs_sentence)
    # pytorch:  students apply these new understanding ##s as they reason about and perform decimal [numbers=0.8328049778938293||##s=0.0865367129445076||operations=0.03134247660636902||placement=0.019931575283408165||places=0.012546995654702187] through the hundred ##ths place .  


def compare_nlptown():
    text = "I like you. I love you"
    id2label = {
        0: "1 star",
        1: "2 stars",
        2: "3 stars",
        3: "4 stars",
        4: "5 stars"
    }
    # ppnlp
    path = "junnyu/nlptown-bert-base-multilingual-uncased-sentiment"
    model = ppnlp.BertForSequenceClassification.from_pretrained(path)
    model.eval()
    tokenizer = ppnlp.BertTokenizer.from_pretrained(path)
    inputs = {
        k: paddle.to_tensor(
            v, dtype="int64").unsqueeze(0)
        for k, v in tokenizer(text).items()
    }
    with paddle.no_grad():
        score = paddle.nn.functional.softmax(model(**inputs), axis=-1)

    for i, s in enumerate(score[0].tolist()):
        label = id2label[i]
        print(f"{label} score {s}")

    # 1 star score 0.0021950288210064173
    # 2 stars score 0.0022533712908625603
    # 3 stars score 0.015475980937480927
    # 4 stars score 0.1935628354549408
    # 5 stars score 0.7865128517150879

    # transformers
    path = "nlptown/bert-base-multilingual-uncased-sentiment"
    model = hgnlp.BertForSequenceClassification.from_pretrained(path)
    model.eval()
    tokenizer = hgnlp.BertTokenizer.from_pretrained(path)

    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        score = torch.nn.functional.softmax(model(**inputs).logits, dim=-1)

    for i, s in enumerate(score[0].tolist()):
        label = id2label[i]
        print(f"{label} score {s}")

    # 1 star score 0.00219502835534513
    # 2 stars score 0.0022533696610480547
    # 3 stars score 0.01547597348690033
    # 4 stars score 0.19356288015842438
    # 5 stars score 0.7865127325057983


def compare_ckiplab_ws():
    text = "??????????????????????????????????????????????????????20???????????????????????????????????????????????????????????????????????????"
    id2label = {"0": "B", "1": "I"}
    # ppnlp
    path = "junnyu/ckiplab-bert-base-chinese-ws"
    model = ppnlp.BertForTokenClassification.from_pretrained(path)
    model.eval()
    tokenizer = ppnlp.BertTokenizer.from_pretrained(path)

    tokenized_text = tokenizer.tokenize(text)
    inputs = {
        k: paddle.to_tensor(
            v, dtype="int64").unsqueeze(0)
        for k, v in tokenizer(text).items()
    }
    with paddle.no_grad():
        score = paddle.nn.functional.softmax(model(**inputs), axis=-1)

    for t, s in zip(tokenized_text, score[0][1:-1]):
        index = paddle.argmax(s).item()
        label = id2label[str(index)]
        print(f"{label} {t} score {s[index].item()}")

    # B ??? score 0.9999865293502808
    # I ??? score 0.999922513961792
    # I ??? score 0.9999332427978516
    # B ??? score 0.9999370574951172
    # B ??? score 0.9983423948287964
    # B ??? score 0.9999731779098511
    # I ??? score 0.9999544620513916
    # B ??? score 0.9999713897705078
    # I ??? score 0.9999532699584961
    # I ??? score 0.9998632669448853
    # B ??? score 0.9999871253967285
    # B ??? score 0.9999560117721558
    # B ??? score 0.9999818801879883
    # I ??? score 0.9999614953994751
    # B ??? score 0.9999759197235107
    # I ??? score 0.9994433522224426
    # B ??? score 0.9999866485595703
    # I ??? score 0.9999630451202393
    # B 20 score 0.9999810457229614
    # B ??? score 0.9974608421325684
    # B ??? score 0.8930220603942871
    # B ??? score 0.9999674558639526
    # B ??? score 0.999970555305481
    # I ??? score 0.9999680519104004
    # B ??? score 0.9997956156730652
    # I ??? score 0.9999778270721436
    # I ??? score 0.9980663657188416
    # B ??? score 0.999984860420227
    # I ??? score 0.999974250793457
    # B ??? score 0.9999891519546509
    # B ??? score 0.999988317489624
    # B ??? score 0.9999889135360718
    # B ??? score 0.9997660517692566
    # B ??? score 0.9999877214431763
    # I ??? score 0.9999549388885498
    # B ??? score 0.9999915361404419
    # I ??? score 0.9980868101119995
    # B ??? score 0.9999058246612549
    # I ??? score 0.9916028380393982
    # I ??? score 0.8443355560302734
    # B ??? score 0.9999363422393799
    # I ??? score 0.9999769926071167
    # I ??? score 0.999947190284729
    # B ??? score 0.9999719858169556

    # ppnlp
    path = "ckiplab/bert-base-chinese-ws"
    model = hgnlp.BertForTokenClassification.from_pretrained(path)
    model.eval()

    tokenizer = hgnlp.BertTokenizer.from_pretrained(path)
    inputs = tokenizer(text, return_tensors="pt")
    tokenized_text = tokenizer.tokenize(text)

    with torch.no_grad():
        score = torch.nn.functional.softmax(model(**inputs).logits, dim=-1)

    for t, s in zip(tokenized_text, score[0][1:-1]):
        index = torch.argmax(s).item()
        label = id2label[str(index)]
        print(f"{label} {t} score {s[index].item()}")

    # B ??? score 0.9999865293502808
    # I ??? score 0.999922513961792
    # I ??? score 0.9999332427978516
    # B ??? score 0.9999370574951172
    # B ??? score 0.9983423948287964
    # B ??? score 0.9999731779098511
    # I ??? score 0.9999544620513916
    # B ??? score 0.9999713897705078
    # I ??? score 0.9999532699584961
    # I ??? score 0.9998632669448853
    # B ??? score 0.9999871253967285
    # B ??? score 0.9999560117721558
    # B ??? score 0.9999818801879883
    # I ??? score 0.9999614953994751
    # B ??? score 0.9999759197235107
    # I ??? score 0.9994433522224426
    # B ??? score 0.9999866485595703
    # I ??? score 0.9999630451202393
    # B 20 score 0.9999810457229614
    # B ??? score 0.9974608421325684
    # B ??? score 0.8930219411849976
    # B ??? score 0.9999674558639526
    # B ??? score 0.999970555305481
    # I ??? score 0.9999680519104004
    # B ??? score 0.9997956156730652
    # I ??? score 0.9999778270721436
    # I ??? score 0.9980663657188416
    # B ??? score 0.999984860420227
    # I ??? score 0.999974250793457
    # B ??? score 0.9999891519546509
    # B ??? score 0.999988317489624
    # B ??? score 0.9999889135360718
    # B ??? score 0.9997660517692566
    # B ??? score 0.9999877214431763
    # I ??? score 0.9999549388885498
    # B ??? score 0.9999915361404419
    # I ??? score 0.9980868101119995
    # B ??? score 0.9999058246612549
    # I ??? score 0.9916029572486877
    # I ??? score 0.8443354964256287
    # B ??? score 0.9999363422393799
    # I ??? score 0.9999769926071167
    # I ??? score 0.999947190284729
    # B ??? score 0.9999719858169556


def compare_ckiplab_pos():
    text = "??????????????????????????????????????????????????????20???????????????????????????????????????????????????????????????????????????"
    id2label = {
        "0": "A",
        "1": "Caa",
        "2": "Cab",
        "3": "Cba",
        "4": "Cbb",
        "5": "D",
        "6": "Da",
        "7": "Dfa",
        "8": "Dfb",
        "9": "Di",
        "10": "Dk",
        "11": "DM",
        "12": "I",
        "13": "Na",
        "14": "Nb",
        "15": "Nc",
        "16": "Ncd",
        "17": "Nd",
        "18": "Nep",
        "19": "Neqa",
        "20": "Neqb",
        "21": "Nes",
        "22": "Neu",
        "23": "Nf",
        "24": "Ng",
        "25": "Nh",
        "26": "Nv",
        "27": "P",
        "28": "T",
        "29": "VA",
        "30": "VAC",
        "31": "VB",
        "32": "VC",
        "33": "VCL",
        "34": "VD",
        "35": "VF",
        "36": "VE",
        "37": "VG",
        "38": "VH",
        "39": "VHC",
        "40": "VI",
        "41": "VJ",
        "42": "VK",
        "43": "VL",
        "44": "V_2",
        "45": "DE",
        "46": "SHI",
        "47": "FW",
        "48": "COLONCATEGORY",
        "49": "COMMACATEGORY",
        "50": "DASHCATEGORY",
        "51": "DOTCATEGORY",
        "52": "ETCCATEGORY",
        "53": "EXCLAMATIONCATEGORY",
        "54": "PARENTHESISCATEGORY",
        "55": "PAUSECATEGORY",
        "56": "PERIODCATEGORY",
        "57": "QUESTIONCATEGORY",
        "58": "SEMICOLONCATEGORY",
        "59": "SPCHANGECATEGORY"
    }
    # ppnlp
    path = "junnyu/ckiplab-bert-base-chinese-pos"
    model = ppnlp.BertForTokenClassification.from_pretrained(path)
    model.eval()
    tokenizer = ppnlp.BertTokenizer.from_pretrained(path)

    tokenized_text = tokenizer.tokenize(text)
    inputs = {
        k: paddle.to_tensor(
            v, dtype="int64").unsqueeze(0)
        for k, v in tokenizer(text).items()
    }
    with paddle.no_grad():
        score = paddle.nn.functional.softmax(model(**inputs), axis=-1)

    for t, s in zip(tokenized_text, score[0][1:-1]):
        index = paddle.argmax(s).item()
        label = id2label[str(index)]
        print(f"{label} {t} score {s[index].item()}")

    # Nb ??? score 0.9999998807907104
    # Nb ??? score 0.9700667858123779
    # Na ??? score 0.9985846281051636
    # Nd ??? score 0.9999947547912598
    # D ??? score 0.9999957084655762
    # VC ??? score 0.9999998807907104
    # VC ??? score 0.9951109290122986
    # Na ??? score 0.9999996423721313
    # Na ??? score 0.9999638795852661
    # VH ??? score 0.9813857674598694
    # COMMACATEGORY ??? score 1.0
    # D ??? score 1.0
    # D ??? score 1.0
    # Cbb ??? score 0.9989008903503418
    # VJ ??? score 0.9999979734420776
    # VC ??? score 0.9965670108795166
    # Nh ??? score 1.0
    # Nh ??? score 1.0
    # Neu 20 score 0.9999995231628418
    # Nf ??? score 0.9125530123710632
    # Ng ??? score 0.9999992847442627
    # P ??? score 1.0
    # Nb ??? score 0.9999996423721313
    # VA ??? score 0.9322434663772583
    # Na ??? score 0.9846553802490234
    # Nc ??? score 0.729569137096405
    # Nc ??? score 0.9999841451644897
    # VC ??? score 0.9999997615814209
    # VC ??? score 0.9999991655349731
    # COMMACATEGORY ??? score 1.0
    # Nh ??? score 0.9999996423721313
    # D ??? score 1.0
    # VK ??? score 1.0
    # Nh ??? score 1.0
    # Nh ??? score 0.9999978542327881
    # Ncd ??? score 0.9856181740760803
    # Ncd ??? score 0.9999995231628418
    # VC ??? score 0.9999988079071045
    # Na ??? score 0.9994786381721497
    # VCL ??? score 0.8332439661026001
    # Nc ??? score 1.0
    # Nc ??? score 0.9999986886978149
    # Nc ??? score 0.9973978996276855
    # PERIODCATEGORY ??? score 1.0

    # transformers
    path = "ckiplab/bert-base-chinese-pos"
    model = hgnlp.BertForTokenClassification.from_pretrained(path)
    model.eval()

    tokenizer = hgnlp.BertTokenizer.from_pretrained(path)
    inputs = tokenizer(text, return_tensors="pt")
    tokenized_text = tokenizer.tokenize(text)

    with torch.no_grad():
        score = torch.nn.functional.softmax(model(**inputs).logits, dim=-1)

    for t, s in zip(tokenized_text, score[0][1:-1]):
        index = torch.argmax(s).item()
        label = id2label[str(index)]
        print(f"{label} {t} score {s[index].item()}")

    # Nb ??? score 0.9999998807907104
    # Nb ??? score 0.970066487789154
    # Na ??? score 0.998584508895874
    # Nd ??? score 0.9999948740005493
    # D ??? score 0.9999957084655762
    # VC ??? score 0.9999998807907104
    # VC ??? score 0.995110809803009
    # Na ??? score 0.9999995231628418
    # Na ??? score 0.9999638795852661
    # VH ??? score 0.9813857674598694
    # COMMACATEGORY ??? score 1.0
    # D ??? score 1.0
    # D ??? score 1.0
    # Cbb ??? score 0.9989006519317627
    # VJ ??? score 0.9999980926513672
    # VC ??? score 0.996566891670227
    # Nh ??? score 1.0
    # Nh ??? score 1.0
    # Neu 20 score 0.9999995231628418
    # Nf ??? score 0.9125524163246155
    # Ng ??? score 0.9999992847442627
    # P ??? score 1.0
    # Nb ??? score 0.9999997615814209
    # VA ??? score 0.9322431087493896
    # Na ??? score 0.9846551418304443
    # Nc ??? score 0.7295736074447632
    # Nc ??? score 0.9999841451644897
    # VC ??? score 0.9999997615814209
    # VC ??? score 0.9999991655349731
    # COMMACATEGORY ??? score 1.0
    # Nh ??? score 0.9999997615814209
    # D ??? score 0.9999998807907104
    # VK ??? score 1.0
    # Nh ??? score 1.0
    # Nh ??? score 0.9999977350234985
    # Ncd ??? score 0.9856180548667908
    # Ncd ??? score 0.9999995231628418
    # VC ??? score 0.9999988079071045
    # Na ??? score 0.9994783997535706
    # VCL ??? score 0.8332419991493225
    # Nc ??? score 1.0
    # Nc ??? score 0.9999988079071045
    # Nc ??? score 0.9973980188369751
    # PERIODCATEGORY ??? score 1.0


def compare_ckiplab_ner():
    text = "??????????????????????????????????????????????????????20???????????????????????????????????????????????????????????????????????????"
    id2label = {
        "0": "O",
        "1": "B-CARDINAL",
        "2": "B-DATE",
        "3": "B-EVENT",
        "4": "B-FAC",
        "5": "B-GPE",
        "6": "B-LANGUAGE",
        "7": "B-LAW",
        "8": "B-LOC",
        "9": "B-MONEY",
        "10": "B-NORP",
        "11": "B-ORDINAL",
        "12": "B-ORG",
        "13": "B-PERCENT",
        "14": "B-PERSON",
        "15": "B-PRODUCT",
        "16": "B-QUANTITY",
        "17": "B-TIME",
        "18": "B-WORK_OF_ART",
        "19": "I-CARDINAL",
        "20": "I-DATE",
        "21": "I-EVENT",
        "22": "I-FAC",
        "23": "I-GPE",
        "24": "I-LANGUAGE",
        "25": "I-LAW",
        "26": "I-LOC",
        "27": "I-MONEY",
        "28": "I-NORP",
        "29": "I-ORDINAL",
        "30": "I-ORG",
        "31": "I-PERCENT",
        "32": "I-PERSON",
        "33": "I-PRODUCT",
        "34": "I-QUANTITY",
        "35": "I-TIME",
        "36": "I-WORK_OF_ART",
        "37": "E-CARDINAL",
        "38": "E-DATE",
        "39": "E-EVENT",
        "40": "E-FAC",
        "41": "E-GPE",
        "42": "E-LANGUAGE",
        "43": "E-LAW",
        "44": "E-LOC",
        "45": "E-MONEY",
        "46": "E-NORP",
        "47": "E-ORDINAL",
        "48": "E-ORG",
        "49": "E-PERCENT",
        "50": "E-PERSON",
        "51": "E-PRODUCT",
        "52": "E-QUANTITY",
        "53": "E-TIME",
        "54": "E-WORK_OF_ART",
        "55": "S-CARDINAL",
        "56": "S-DATE",
        "57": "S-EVENT",
        "58": "S-FAC",
        "59": "S-GPE",
        "60": "S-LANGUAGE",
        "61": "S-LAW",
        "62": "S-LOC",
        "63": "S-MONEY",
        "64": "S-NORP",
        "65": "S-ORDINAL",
        "66": "S-ORG",
        "67": "S-PERCENT",
        "68": "S-PERSON",
        "69": "S-PRODUCT",
        "70": "S-QUANTITY",
        "71": "S-TIME",
        "72": "S-WORK_OF_ART"
    }
    # ppnlp
    path = "junnyu/ckiplab-bert-base-chinese-ner"
    model = ppnlp.BertForTokenClassification.from_pretrained(path)
    model.eval()
    tokenizer = ppnlp.BertTokenizer.from_pretrained(path)

    tokenized_text = tokenizer.tokenize(text)
    inputs = {
        k: paddle.to_tensor(
            v, dtype="int64").unsqueeze(0)
        for k, v in tokenizer(text).items()
    }
    with paddle.no_grad():
        score = paddle.nn.functional.softmax(model(**inputs), axis=-1)

    for t, s in zip(tokenized_text, score[0][1:-1]):
        index = paddle.argmax(s).item()
        label = id2label[str(index)]
        print(f"{label} {t} score {s[index].item()}")

    # B-PERSON ??? score 0.9999995231628418
    # I-PERSON ??? score 0.9999994039535522
    # E-PERSON ??? score 0.9999995231628418
    # B-DATE ??? score 0.9991734623908997
    # O ??? score 0.9852147698402405
    # O ??? score 1.0
    # O ??? score 0.9999998807907104
    # O ??? score 0.9999996423721313
    # O ??? score 0.9999997615814209
    # O ??? score 0.9999997615814209
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # B-DATE 20 score 0.9999992847442627
    # E-DATE ??? score 0.9999892711639404
    # O ??? score 0.9999995231628418
    # O ??? score 1.0
    # B-ORG ??? score 0.9999990463256836
    # I-ORG ??? score 0.9999986886978149
    # I-ORG ??? score 0.999998927116394
    # I-ORG ??? score 0.9999985694885254
    # E-ORG ??? score 0.999998927116394
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 0.9999960660934448

    # transformers
    path = "ckiplab/bert-base-chinese-ner"
    model = hgnlp.BertForTokenClassification.from_pretrained(path)
    model.eval()

    tokenizer = hgnlp.BertTokenizer.from_pretrained(path)
    inputs = tokenizer(text, return_tensors="pt")
    tokenized_text = tokenizer.tokenize(text)

    with torch.no_grad():
        score = torch.nn.functional.softmax(model(**inputs).logits, dim=-1)

    for t, s in zip(tokenized_text, score[0][1:-1]):
        index = torch.argmax(s).item()
        label = id2label[str(index)]
        print(f"{label} {t} score {s[index].item()}")

    # B-PERSON ??? score 0.9999996423721313
    # I-PERSON ??? score 0.9999994039535522
    # E-PERSON ??? score 0.9999995231628418
    # B-DATE ??? score 0.9991734623908997
    # O ??? score 0.9852147698402405
    # O ??? score 1.0
    # O ??? score 0.9999998807907104
    # O ??? score 0.9999997615814209
    # O ??? score 1.0
    # O ??? score 0.9999998807907104
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # B-DATE 20 score 0.9999994039535522
    # E-DATE ??? score 0.9999892711639404
    # O ??? score 0.9999996423721313
    # O ??? score 1.0
    # B-ORG ??? score 0.9999991655349731
    # I-ORG ??? score 0.9999986886978149
    # I-ORG ??? score 0.999998927116394
    # I-ORG ??? score 0.9999984502792358
    # E-ORG ??? score 0.999998927116394
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 1.0
    # O ??? score 0.9999960660934448


if __name__ == "__main__":
    compare_ckiplab_ner()
    compare_ckiplab_pos()
    compare_ckiplab_ws()
    compare_math()
    compare_nlptown()
