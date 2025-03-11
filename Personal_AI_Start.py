from Personal_AI import CHAT_BOT

Chat = CHAT_BOT(
    FunchControl=1,
    Esik_Data_Control=0.8,
    Esik_Data_True=0.7,
    WhileControl=True,
    Input_diff_cont=False,
    vouse_cont=True,
    Thread_Sleep=0.05,
    dataControl = True)

FunchControl = Chat.FunchControl

if __name__ == "__main__" :

    if FunchControl == 1 : Chat.threading_Start()

    