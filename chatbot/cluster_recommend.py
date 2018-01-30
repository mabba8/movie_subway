import pickle
from pymongo import MongoClient
from scipy import spatial
import operator

class ClusterRecommend:
    info = {}
    user_select = {'cluster': '-1',
                   'tags': list(),
                   'rel': list()}
    tname_tindex = {}

    def __init__(self):
        with open('chatbot/rsc/c_info_SHORT.pkl', 'rb') as f:
            a = pickle.load(f)
        self.info = a
        with open('chatbot/rsc/tagname_index_dictII', 'rb') as f:
            a = pickle.load(f)
        self.tname_tindex = a

    def getCname(self):
        result = []
        for k in self.info.keys():
            result.append(self.info[k]['name'])
        return result

    def getTags(self, cid):
        result = []
        num = 1
        for tag in self.info[cid]['tags']:
            text = '{}.{}'.format(num, tag)
            result.append(text)
            num += 1
        return result

    def setCluster(self,cid):
        self.user_select['cluster'] = cid

    def setTags(self, selected_str):
        selected_num = selected_str.split(' ')
        selected_name = []
        for num in selected_num:
            dict = self.info[self.user_select['cluster']]['tags']
            selected_name.append(dict[int(num) - 1])
        self.user_select['tags'] = selected_name

    def setRel(self):
        select_index = []
        for tname in self.user_select['tags']:
            select_index.append(self.tname_tindex[tname])
        insert_dict = {}
        rel_list = self.info[self.user_select['cluster']]['rel_default']
        for index in select_index:
            insert_dict[index] = 100
            # if rel_list[index] * 1.5 > 1:
            #     insert_dict[index] = 0.9
            # else:
            #     insert_dict[index] = rel_list[index] * 1.5
        insert_rel = []
        for rel in rel_list:
            insert_rel.append(rel)
        for k, v in insert_dict.items():
            insert_rel[k] = v
        self.user_select['rel'] = insert_rel

    def getMovies(self):
        client = MongoClient("localhost", 27017)
        db = client["bb104t1"]
        collection = db['movieInfo']
        q_result =  collection.find({'cid':int(self.user_select['cluster'])}, {'_id': 0,'chname': 1,'enname': 1, 'rel': 1})
        q_rel = []
        for doc in q_result:
            chname = doc['chname']
            enname = doc['enname']
            cosSim = 1 - spatial.distance.cosine(doc['rel'], self.user_select['rel'])
            t = (cosSim, chname, enname)
            q_rel.append(t)
        q_rel = sorted(q_rel, key=operator.itemgetter(0), reverse=True)
        resutl = []
        for t in q_rel[0:3]:
            resutl.append(t)
        return resutl