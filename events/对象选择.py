def event_对象选择(self):
    charalist=[]
    gradient_text = ""
    ImgList=[]
    for i in self.console.init.chara_ids:
        if self.charater_pwds.get(i).get('小地图') == self.charater_pwds.get('0').get('小地图') :
            charalist.append(i)
    for i in charalist:
        charaname= self.console.init.charaters_key.get(i).get('名前')
        gradient_text += self.cs(charaname).click(i) + "   "
        ImgList.append()
    return gradient_text