class message:
    text="はじめの値"
    text2="いえー"

    def add(self):
        return self.message + self.text2


def overwrite(mes):
    print(f"関数に入った時点では{mes.text}")
    mes.text="関数で変更しました"
    print(f"関数の中で {mes.text}")
    print(f"テキスト2は{mes.text2}")
    mes.text2="テキスト2も変更しました"
    print(f"テキスト2は{mes.text2}")

m = message()
m.text="クラスを作った後変更"
m.text2="テキスト2ってつくれるのかな"
overwrite(m)
print(f"関数の外でも、{m.text}")
print(f"テキスト2は{m.text2}")
print(message.add)
