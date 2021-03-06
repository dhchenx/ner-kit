import stanza
from stanza.server import CoreNLPClient, StartServer
from stanza.models.common.doc import Document
from stanza.pipeline.core import Pipeline
from stanza.pipeline.multilingual import MultilingualPipeline


def install_corenlp(corenlp_root_path):
    stanza.install_corenlp(
        dir=corenlp_root_path)

def get_entity_list(text,corenlp_root_path="", language="chinese",memory='6G',timeout=300000):
    if corenlp_root_path!="":
        stanza.install_corenlp(
            dir=corenlp_root_path)

    client = CoreNLPClient(
        start_server=StartServer.TRY_START,
        annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'depparse', 'coref'],
        timeout=timeout,
        memory=memory,
        properties=language,
        # StartServer=StartServer.TRY_START
    )
    list_token = []
    ann = client.annotate(text)
    for sentence in ann.sentence:
        for token in sentence.token:
            print(token.value, token.pos, token.ner)
            token_model = {
                "value": token.value,
                "pos": token.pos,
                "ner": token.ner
            }
            list_token.append(token_model)
    return list_token

class StanzaWrapper:
    def __init__(self,auto_download_en=True,auto_download_zh=True,should_print_msg=False):
        if auto_download_en:
            self.download(lang="en")
        if auto_download_zh:
            self.download_chinese_model()
        self.should_print_result=should_print_msg

    def download(self,lang="en",processors="tokenize,pos",verbose=False):
        stanza.download(lang,processors=processors,verbose=verbose)

    def download_chinese_model(self,lang='zh',verbos=False):
        stanza.download(lang=lang,verbose=verbos)

    def tokenize(self,text,lang="en",processors="tokenize",tokenize_no_ssplit=False,tokenize_pretokenized=False):
        nlp = stanza.Pipeline(lang=lang, processors=processors,tokenize_no_ssplit=tokenize_no_ssplit,tokenize_pretokenized=tokenize_pretokenized)
        doc = nlp(text)
        list_sentence=[]
        for i, sentence in enumerate(doc.sentences):
            if self.should_print_result:
                print(f'====== Sentence {i + 1} tokens =======')
                print(*[f'id: {token.id}\ttext: {token.text}' for token in sentence.tokens], sep='\n')
            tokens=[]
            for token in sentence.tokens:
                model={
                    "id":token.id,
                    "text":token.text
                }
                tokens.append(model)
            list_sentence.append(tokens)
        return list_sentence

    def tokenize_list(self,list_tokens,lang="en",processors="tokenize",tokenize_no_ssplit=False,tokenize_pretokenized=False):
        nlp = stanza.Pipeline(lang=lang, processors=processors,tokenize_no_ssplit=tokenize_no_ssplit,tokenize_pretokenized=tokenize_pretokenized)
        doc = nlp(list_tokens)
        list_sentence=[]
        for i, sentence in enumerate(doc.sentences):
            if self.should_print_result:
                print(f'====== Sentence {i + 1} tokens =======')
                print(*[f'id: {token.id}\ttext: {token.text}' for token in sentence.tokens], sep='\n')
            tokens=[]
            for token in sentence.tokens:
                model = {
                    "id": token.id,
                    "text": token.text
                }
                tokens.append(model)
            list_sentence.append(tokens)
        return list_sentence

    def tokenize_by_spacy(self,text):
        processors={"tokenize":'spacy'}
        nlp = stanza.Pipeline(lang='en', processors=processors)
        doc = nlp(text)
        list_sentence=[]
        for i, sentence in enumerate(doc.sentences):
            if self.should_print_result:
                print(f'====== Sentence {i + 1} tokens =======')
                print(*[f'id: {token.id}\ttext: {token.text}' for token in sentence.tokens], sep='\n')
            tokens=[]
            for token in sentence.tokens:
                model = {
                    "id": token.id,
                    "text": token.text
                }
                tokens.append(model)
            list_sentence.append(tokens)
        return list_sentence

    def mwt_expand(self,text,lang='en',processors='tokenize,mwt'):

        nlp = stanza.Pipeline(lang=lang, processors=processors)
        doc = nlp(text)
        list_result=[]
        for sentence in doc.sentences:
            list_token=[]
            for token in sentence.tokens:
                if self.should_print_result:
                    print(f'token: {token.text}\twords: {", ".join([word.text for word in token.words])}')
                model={
                    "token":token.text,
                    "text":", ".join([word.text for word in token.words])
                }
                list_token.append(model)
            list_result.append(list_token)
        return list_result

    def tag_chinese(self,text,lang='zh',processors='tokenize,lemma,pos,depparse'):
        return self.tag(text,lang,processors)

    def tag(self,text,lang='en',processors='tokenize,mwt,pos'):
        nlp = stanza.Pipeline(lang=lang, processors=processors)
        doc = nlp(text)
        if self.should_print_result:
            print(
                *[f'word: {word.text}\tupos: {word.upos}\txpos: {word.xpos}\tfeats: {word.feats if word.feats else "_"}' for
                  sent in doc.sentences for word in sent.words], sep='\n')
        list_result=[]
        for sent in doc.sentences:
            for word in sent.words:
                model={
                    "word":word.text,
                    "upos":word.upos,
                    "xpos":word.upos,
                    "feats":word.feats if word.feats else "_"
                }
                list_result.append(model)
        return list_result

    def parse_dependency_chinese(self,text,lang='zh',processors='tokenize,lemma,pos,depparse'):
        return self.parse_dependency(text,lang,processors)

    def parse_dependency(self,text,lang='en',processors='tokenize,mwt,pos,lemma,depparse'):
        nlp = stanza.Pipeline(lang=lang, processors=processors)
        doc = nlp(text)
        if self.should_print_result:
            print(*[
            f'id: {word.id}\tword: {word.text}\thead id: {word.head}\thead: {sent.words[word.head - 1].text if word.head > 0 else "root"}\tdeprel: {word.deprel}'
            for sent in doc.sentences for word in sent.words], sep='\n')
        list_result = []
        for sent in doc.sentences:
            for word in sent.words:
                model = {
                    "id": word.id,
                    "text": word.text,
                    "head id": word.head,
                    "head": sent.words[word.head - 1].text if word.head > 0 else "root",
                    "deprel":word.deprel
                }
                list_result.append(model)
        return list_result

    def ner(self,text,lang='en',processors='tokenize,ner'):
        nlp = stanza.Pipeline(lang=lang, processors=processors)
        doc = nlp(text)
        if self.should_print_result:
            print(*[f'entity: {ent.text}\ttype: {ent.type}' for ent in doc.ents], sep='\n')
        list_result=[]
        for ent in doc.ents:
            model={
                "entity":ent.text,
                "type":ent.type
            }
            list_result.append(model)
        return list_result

    def ner_chinese(self,text,lang='zh',processors='tokenize,ner'):
        return self.ner(text,lang,processors)

    def ner_token_chinese(self,text,lang='zh',processors='tokenize,ner'):
        return self.ner_token(text,lang,processors)

    def ner_token(self,text,lang='en',processors='tokenize,ner'):
        nlp = stanza.Pipeline(lang=lang, processors=processors)
        doc = nlp(text)
        if self.should_print_result:
            print(*[f'token: {token.text}\tner: {token.ner}' for sent in doc.sentences for token in sent.tokens], sep='\n')
        list_result=[]
        for sent in doc.sentences:
            for token in sent.tokens:
                model = {
                    "token": token.text,
                    "ner": token.ner
                }
                list_result.append(model)
        return list_result

    def sentiment_chinese(self,text,lang='zh',processors='tokenize,sentiment'):
        return self.sentiment(text,lang=lang,processors=processors)

    def sentiment(self,text,lang='en',processors='tokenize,sentiment'):
        nlp = stanza.Pipeline(lang=lang, processors=processors)
        doc = nlp(text)
        list_result=[]
        for i, sentence in enumerate(doc.sentences):
            # print(i, sentence.sentiment)
            model={
                "sentence":sentence.text,
                "sentiment":sentence.sentiment
            }
            list_result.append(model)
        return list_result

    def lang(self,list_text,lang="multilingual",langid_clean_text=False):
        stanza.download(lang="multilingual")
        nlp = Pipeline(lang=lang, processors="langid",langid_clean_text=langid_clean_text)
        docs =list_text
        docs = [Document([], text=text) for text in docs]
        nlp(docs)
        if self.should_print_result:
            print("\n".join(f"{doc.text}\t{doc.lang}" for doc in docs))
        list_result=[]
        for doc in docs:
            model={
                "text":doc.text,
                "lang":doc.lang
            }
            list_result.append(model)
        return list_result

    def lang_multi(self,list_text,func_process=None,download_lang=""):
        if download_lang!="":
            for l in download_lang.split(","):
                stanza.download(lang=l)
        nlp = MultilingualPipeline()
        docs=list_text
        docs = nlp(docs)
        list_result=[]
        for doc in docs:
            if  self.should_print_result:
                print("---")
                print(f"text: {doc.text}")
                print(f"lang: {doc.lang}")
                print(f"{doc.sentences[0].dependencies_string()}")
            model={
                "text":doc.text,
                "lang":doc.lang,
                "doc":doc
            }
            if func_process!=None:
                func_process(model)
            list_result.append(model)
        return list_result

    def print_result(self,result):
        if result==None or len(result)==0:
            print("No Result!")
            return
        for idx,item in enumerate(result):
            print(idx)
            if type(item)==dict:
                fields = list(result[0].keys())
                print('\t\t'+ '\t'.join(fields))
                list_v=[]
                for k in item.keys():
                    list_v.append(str(item[k]))
                line = '\t'.join(list_v)
                print(f"\t\t{line}")
            elif type(item)==list:
                fields = list(item[0].keys())
                print('\t\t' + '\t'.join(fields))
                for idx1,li in enumerate(item):
                    # print('\t-',idx1)
                    if type(li)==dict:
                        list_v=[]
                        for k in li.keys():
                            list_v.append(str(li[k]))
                            # print(f"\t\t{k}\t{li[k]}")
                        line='\t'.join(list_v)
                        print(f"\t\t{line}")
                    else:
                        print('\t\t',li)
