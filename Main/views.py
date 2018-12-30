from django.shortcuts import render
import networkx as nx
from networkx.readwrite import json_graph
import json
import tweepy
# API 1
consumer_key = "__put your consumer_key here__"
consumer_secret = "__put your consumer_secret here__"
access_token = "__put your access_token here__"
access_token_secret = "__put your access_token_secret here__"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

cont = {}
dic,dic2 = [],[]

# Friends List
def friend_list(user):
    try:
        if(api.get_user(user)._json['followers_count'] < 1000 and api.get_user(user)._json['friends_count'] < 1000):
            following = set(api.friends_ids(user,[-1]))
            followers = set(api.followers_ids(user,[-1]))
            friends = following.intersection(followers)
            if(friends == set()):
                return 'Null'
            return friends
        else:
            return 'Null'
    except:
        print("Limit null")
        return set()

# Graph
def user_graph(user_id,friends):
    g = nx.Graph()
    for i in friends:
        g.add_edge(user_id,i)
    return g

# compose
def full_graph(s,m):
    G = nx.compose(s,m)
    return G

# compare
def compare(sg,tg):
    com = set(sg.nodes()).intersection(set(tg.nodes()))
    return com

def getUser(request):
    if request.method == 'GET':
        return render(request, 'user.html', {})

    else:
        global api
        api = tweepy.API(auth2)
        sou = request.POST.get('source')
        tar = request.POST.get('target')
        source = api.get_user(sou)._json['id']
        target = api.get_user(tar)._json['id']
        source_graph = nx.Graph()
        source_graph.add_node(source)
        target_graph = nx.Graph()
        target_graph.add_node(target)
        common_set = compare(source_graph,target_graph)
        source_list,target_list = [source],[target]
        flag = False
        s_null,t_null = 0,0
        if(common_set == set()):
            while(True):
                if(source_list != [] or target_list != []):
                    # Source
                    temp = source_list.copy()
                    source_list.clear()
                    for sf in temp:
                        if(s_null >= 2):
                            print("Source Null Sets")
                            s_null = 0
                            break
                        if(s_null == 1):
                            #print("Source API Change")
                            print("api limit end")
                            #api = tweepy.API(auth2)
                        childs = friend_list(sf)
                        if(childs == 'Null'):
                            continue
                        if(childs != set()):
                            source_list += childs
                            for c in childs.copy():
                                if(source_graph.has_node(c)):
                                    childs.remove(c)
                            sf_graph = user_graph(sf,childs)
                            source_graph = full_graph(source_graph,sf_graph)
                        else:
                            s_null += 1
                    print(source_list)
                    # Target
                    api = tweepy.API(auth)
                    temp2 = target_list.copy()
                    target_list.clear()
                    for tf in temp2:
                        if(t_null >= 2):
                            print("Target Null Sets")
                            t_null = 0
                            break
                        if(t_null == 1):
                            print("Target API Change")
                            api = tweepy.API(auth2)
                        t_childs = friend_list(tf)
                        if(t_childs == 'Null'):
                            continue
                        if(t_childs != set()):
                            target_list += t_childs
                            for d in t_childs.copy():
                                if(target_graph.has_node(d)):
                                    t_childs.remove(d)
                            tf_graph = user_graph(tf,t_childs)
                            target_graph = full_graph(target_graph,tf_graph)
                        else:
                            t_null += 1
                    print(target_list)
                else:
                    print("Null sets")
                    flag = True
                G = compare(source_graph,target_graph)
                if(G != set()):
                    print("yes")
                    main_graph = full_graph(source_graph,target_graph)
                    final_path = nx.shortest_path(main_graph,source=source,target=target)
                    for i in final_path:
                        dic.append(api.get_user(i)._json['screen_name'])
                    break
                else:
                    #print("###################################################################################################")
                    api = tweepy.API(auth)
                if(flag == True):
                    print("Limit Exceeds")
                    break
            a = dic.copy()
            co = 0
            temp = '{ "nodes":  ['
            for i in a:
                temp += '{ "id": "'+str(i)+'"}'
                if(co != len(a)-1):
                    temp += ','
                else:
                    temp += ']'
                    co = 0
                co += 1
            temp += ', "links": ['
            for i in range(len(a)-1):
                temp += '{"source": '+str(i)+', "target": '+str(i+1)+'}'
                if(co != len(a)-1):
                    temp += ','
                else:
                    temp += ']'
                    co = 0
                co += 1
            temp += '}'
            f = open("..static\\data.json",'w')
            f.write(temp)
            f.close()
            dic2 = dic.copy()
            dic.clear()

        cont = {
            'source': request.POST.get('source'),
            'target': request.POST.get('target'),
            'user_path':dic2
                    #'flag': request.POST.get('flag'),
                    #'pp': request.POST.get('prakhar_graph')
                }
        return render(request, 'graph.html', cont)
