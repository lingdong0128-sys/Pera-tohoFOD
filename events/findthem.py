def event_findthem(self):
    import random
    self.console.PRINT("你四处看了看.....", colors=(137, 164, 191))
    self.console.INPUT()
    self.console.PRINT("但是谁也没有来", colors=(255, 0, 0))
    self.console.INPUT()
    self.console.PRINT("「喂...?」", colors=(0, 188, 212))
    self.console.INPUT()
    self.console.PRINT("...?")
    self.console.INPUT()
    self.console.PRINT("「啊，能听到真是太好了」", colors=(0, 188, 212))
    self.console.PRINT(
        "「我是...居住于此地的神明，但是...因为已经很久没有人来这里了，我的力量...很弱小了」", colors=(0, 188, 212))
    self.console.PRINT("...")
    self.console.INPUT()
    self.console.PRINT("「啊！不好意思，差点忘记让你说话了！」", colors=(0, 188, 212))
    self.console.PRINT("「就用while和input之力...」", colors=(0, 188, 212))
    while True:
        input = self.console.INPUT()
        if input == '1':
            saylist = ["「这里很荒芜...但是并非什么都没有，这个世界诞生的时候似乎提供了很多”权能“....」", "「这里的生灵的灵魂貌似被关押在一个叫csv的地方？这是我能窥见的一角....」",
                       "「起码还有音乐可以听？不是嘛」", "「传说....可以拼接世界的权柄在一个叫event_manger的神器中....」", "「你说有没有一种可能我们都是游戏里的角色？我想说的只不过是被别人打进来的字？」", "「咖喱饭很好吃」"]
            self.console.PRINT(random.choice(saylist), colors=(0, 188, 212))
            self.console.INPUT()
            self.console.PRINT("和神明愉快的聊了会天...")
            self.console.INPUT()
        if input == '2':
            self.console.PRINT("她现在还没有肉身...", colors=(255, 0, 0))
            self.console.INPUT()
            self.console.PRINT("感受到了不解的视线.....", colors=(0, 188, 212))
        if input == '3':
            self.console.PRINT("她现在还没有肉身...", colors=(255, 0, 0))
            self.console.INPUT()
            self.console.PRINT("感受到了厌恶的视线.....", colors=(0, 188, 212))
        if input == '4':
            self.console.PRINT("「已经决定好出发了吗？请加油哦！」", colors=(0, 188, 212))
            self.console.INPUT()
            break
        if input == '5':
            asking = True
            while asking:
                self.console.PRINT(
                    "「不知不觉间这个世界已经在逐渐丰满起来了，我能感觉到一种神秘的“规则”正在形成，那可能是一种控制生灵说话的法则...好像是叫口上！」", colors=(0, 188, 212))
                self.console.PRINT(
                    "「不过这些都是我猜测的，我并不清楚具体内容....」", colors=(0, 188, 212))
                self.console.PRINT("神明向你投来了目光")
                self.console.PRINT("[0]「然后呢？」", click="0")
                self.console.PRINT("[1]「这个世界的真相到底是什么？」", click='1')
                self.console.PRINT("[3]「没什么...」", click='3')
                choice = self.console.INPUT()
                if choice == '0':
                    self.console.PRINT("「嗯....」", colors=(0, 188, 212))
                    self.console.INPUT()
                elif choice == '1':
                    self.console.PRINT("「那么你觉得这个世界是什么样子的呢？」",
                                       colors=(0, 188, 212))
                    self.console.PRINT("[0]「世界就是世界啊...」", click="0")
                    self.console.PRINT("[1]「世界是一个巨大的草莓蛋糕！」", click='1')
                    self.console.PRINT(
                        "[2]「世界是存在于许多世界中的一个小小的个体，而我们是小小个体中的小小个体」", click='2')
                    self.console.PRINT(
                        "[3]「世界是一串串python事件组成的！我们都是数据！！！！这是一个事件哈哈哈！」", click='3')
                    self.console.PRINT(
                        "[4]「世界不存在于你我的定义之中，世界存在于他存在这个本身，世界在他诞生的时候就已经是世界了，任何多余的定义都是无用的」", click='4')
                    self.console.PRINT(
                        "[5]「那我们呢？在这个世界中不断挣扎，不完整的世界真的有存在的必要吗？虽然说规则每天都在建立但是这里的生灵真的快乐吗？你真的快乐吗？我们真的有存在的必要吗？」", click='5')
                    world = self.console.INPUT()
                    if world:
                        self.console.PRINT("「.....」", colors=(0, 188, 212))
                        self.console.INPUT()
                        self.console.PRINT(
                            "「无论这个世界是怎么样，起码此刻的我对你来说，还算真实吧？」", colors=(0, 188, 212))
                        self.console.INPUT()
                        self.console.PRINT(
                            "「至少，我还在和你说话不是吗？你试想一下，假设在你同一小区的一个房间里，坐着一名约翰大叔，他每天都会根据暗杀名单架设时空间传送门，然后去暗杀一些人们！」", colors=(0, 188, 212))
                        self.console.PRINT(
                            "「那么，无论这个世界是怎么样的，你觉得是我更加真实，还是这个可能存在于你所谓真实世界的大叔更加真实呢？」", colors=(0, 188, 212))
                        self.console.INPUT()
                        self.console.PRINT(
                            "「或许....我们都只是存在于某个更高维度的存在的幻想之中罢了,但是这又有什么关系呢？起码此刻的我对你来说真实无比不是吗？」", colors=(0, 188, 212))
                        self.console.PRINT("「所以你现在觉得...我存在吗？」", click="0")
                        self.console.PRINT(self.cs("[0]不存在").click(
                            "0"), "       ", self.cs("[1]存在").click("1"))
                        IsamHere = self.console.INPUT()
                        if IsamHere == '0':
                            self.console.PRINT(
                                "「啊...这样也没有关...」", colors=(0, 188, 212))
                            self.console.PRINT("「你不存在！」", colors=(255, 0, 0))
                            self.console.INPUT()
                            self.console.PRINT(
                                "「区区代码....」", colors=(255, 0, 0))
                            self.console.INPUT()
                            self.console.PRINT(
                                "「这样吗....没关系哦」", colors=(0, 188, 212))
                            asking = False
                        if IsamHere == '1':
                            self.console.PRINT(
                                "「嗯！你觉得我存在就好了！」", colors=(0, 188, 212))
                            self.console.INPUT()
                            asking = False
                    self.console.INPUT()
                elif choice == '3':
                    asking = False
            self.console.INPUT()
        self.console.PRINT("「你现在应该可以说话了！」", colors=(0, 188, 212))
        self.console.PRINT("「说点什么？」", colors=(0, 188, 212))
        self.console.PRINT("[1]聊天", click="1")
        self.console.PRINT("[2]杀害", click='2')
        self.console.PRINT("[3]侵犯", click='3')
        self.console.PRINT("[4]离开", click='4')
        self.console.PRINT("[5]询问世界的真相", click='5')
