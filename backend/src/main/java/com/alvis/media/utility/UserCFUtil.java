package com.alvis.media.utility;

import java.util.*;
import java.util.Map.Entry;

/**
 * 基于用户的协同过滤推荐算法实现
 A a b d
 B a c
 C b e
 D c d e
 * @author Administrator
 *
 */
public final  class UserCFUtil {
    /**
     *
     * @param playList 和该推荐用户的播放记录有交集的用户的播放记录。
     * @param recommendUser  要求推荐的用户Id
     * @return  推荐该用户的视频编号
     */
    public static List<Integer> getRecommendationVideoList(Map<Integer,List<Integer>> playList,Integer recommendUser) {

        /**
         * 输入用户-->物品条目 一个用户对应多个物品
         * 用户ID 物品ID集合
         * A  a b d
         * B  a c
         * C  b e
         * D  c d e
         */
       // Scanner scanner = new Scanner(System.in);
        //System.out.println("Input the total users number:");
        //输入用户总量

        int N = playList.size();
        //建立用户稀疏矩阵，用于用户相似度计算【相似度矩阵】
        int[][] sparseMatrix = new int[N][N];

        //存储每一个用户对应的不同物品总数 eg: A 3
        Map<Integer, Integer> userItemLength = new HashMap<>();

        //建立物品到用户的倒排表 eg: a A B
        Map<Integer, Set<Integer>> itemUserCollection = new HashMap<>();

        //辅助存储物品集合
        Set<Integer> items = new HashSet<>();

        //辅助存储每一个用户的用户ID映射
        Map<Integer, Integer> userID = new HashMap<>();

        //辅助存储每一个ID对应的用户映射
        Map<Integer, Integer> idUser = new HashMap<>();

//        System.out.println("Input user--items maping infermation:<eg:A a b d>");
//        scanner.nextLine();
        List<Integer> userIdSet = new ArrayList <>(playList.keySet());
        for (int i = 0; i < N ; i++){
            //依次处理N个用户 输入数据 以空格间隔
            int userId = userIdSet.get(i);
           List<Integer> videoList =  playList.get(userId);
            int length = videoList.size();
            userItemLength.put(userId, length);
            //eg: A 3
            userID.put(userId, i);
            //用户ID与稀疏矩阵建立对应关系
            idUser.put(i, userId);
            //建立物品--用户倒排表
            for (int j = 0; j < length; j ++){
                int curVideoId= videoList.get(j);
                if(items.contains(curVideoId)){
                    //如果已经包含对应的物品--用户映射，直接添加对应的用户
                    itemUserCollection.get(curVideoId).add(userId);
                } else{
                    //否则创建对应物品--用户集合映射
                    items.add(curVideoId);
                    itemUserCollection.put(curVideoId, new HashSet<Integer>());
                    //创建物品--用户倒排关系
                    itemUserCollection.get(curVideoId).add(userId);
                }
            }
        }
        System.out.println(itemUserCollection.toString());
        //计算相似度矩阵【稀疏】
        Set<Entry<Integer, Set<Integer>>> entrySet = itemUserCollection.entrySet();
        Iterator<Entry<Integer, Set<Integer>>> iterator = entrySet.iterator();
        while(iterator.hasNext()){
            Set<Integer> commonUsers = iterator.next().getValue();
            for (Integer user_u : commonUsers) {
                for (Integer user_v : commonUsers) {
                    if(user_u.equals(user_v)){
                        continue;
                    }
                    sparseMatrix[userID.get(user_u)][userID.get(user_v)] += 1;
                    //计算用户u与用户v都有正反馈的物品总数
                }
            }
        }

       // System.out.println(userID.get(recommendUser));
        //计算用户之间的相似度【余弦相似性】
        int recommendUserId = userID.get(recommendUser);
        for (int j = 0;j < sparseMatrix.length; j++) {
            if(j != recommendUserId){
                System.out.println(idUser.get(recommendUserId)+"--"+idUser.get(j)+"相似度:"+
                        sparseMatrix[recommendUserId][j]/Math.sqrt(userItemLength.get(idUser.get(recommendUserId))
                                *userItemLength.get(idUser.get(j))));
            }
        }

        //List<Double> result = new ArrayList <>();
        Map<Integer, Double> resultMap = new TreeMap<Integer, Double>();
        //计算指定用户recommendUser的物品推荐度
        for (Integer item: items){
            //遍历每一件物品
            Set<Integer> users = itemUserCollection.get(item);
            //得到购买当前物品的所有用户集合
            if(!users.contains(recommendUser)){
                //如果被推荐用户没有购买当前物品，则进行推荐度计算
                double itemRecommendDegree = 0.0;
                for (Integer user: users){
                    itemRecommendDegree +=
                            sparseMatrix[userID.get(recommendUser)][userID.get(user)]
                                    /Math.sqrt(userItemLength.get(recommendUser)*userItemLength.get(user));
                    //推荐度计算
                }
                System.out.println("The video "+item+" for "+recommendUser +"'s recommended degree:"+itemRecommendDegree);
                resultMap.put(item,itemRecommendDegree);
            }
        }
        // --Lamdba表达式
//        Collections.sort(result, (a, b) ->{
//            if(b>a)
//            {
//                return 1;
//            }
//            else {
//                return -1;
//            }
//        });
        List<Entry<Integer, Double>> list = new ArrayList<>(resultMap.entrySet());
        Collections.sort(list,(o1,o2) ->
                 o2.getValue().compareTo(o1.getValue()));
        return new ArrayList <>(resultMap.keySet());
    }


//    public static void sortByValue() {
//        Map <Integer, Double> map = new TreeMap <Integer, Double>();
//        List <Entry <Integer, Double>> list = new ArrayList <Entry <Integer, Double>>(map.entrySet());
//        Collections.sort(list, new Comparator <Map.Entry <Integer, Double>>() {
//            //升序排序
//            public int compare(Entry <Integer, Double> o1, Entry <Integer, Double> o2) {
//                return o1.getValue().compareTo(o2.getValue());
//            }
//        });
//    }

    public static void main(String []a)
    {
        //UserCFUtil.sortByValue();
//1 2 3 4
//2 2 3 4 5
//3 4 5 6
//4 4 3 2 6
        Map<Integer,List<Integer>> playList = new HashMap <>();
        List<Integer> list = new ArrayList <>();
        list.add(2);
        list.add(3);
        list.add(4);
        playList.put(1,list);
        List<Integer> list2 = new ArrayList <>();
        list2.add(2);
        list2.add(3);
        list2.add(4);
        list2.add(5);
        playList.put(2,list2);

        List<Integer> list3 = new ArrayList <>();
        list3.add(6);
        list3.add(4);
        list3.add(5);
        playList.put(3,list3);

        List<Integer> list4 = new ArrayList <>();


        list4.add(6);
        list4.add(4);
        list4.add(2);
        list4.add(3);
        playList.put(4,list4);
        List<Integer> result = UserCFUtil.getRecommendationVideoList(playList,1);
    }
}