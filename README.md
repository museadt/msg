# 通知系统

一个简洁的通知系统，包含服务端和PC客户端，支持文本、图片和图文混排消息的发送和接收。

从架构开始的介绍基本上都不可能太准了。全是用AI折腾出来的。。

就是个简单的通知系统，服务端接收消息，客户端显示消息。消息保存在服务端，运行后会自己建数据库的，每10天还是30天自己清数据库，具体多少天记不清了，有能力的自己看代码

暂时这东西算是能用了，等我自己慢慢用，慢慢改吧，github我基本上就是不会用，都在网页端传上来的，这些个缓冲问题，会不会导致代码无效，我也不知道了。

python3.8的32位版，我其实是个写游戏脚本的，DDDD。。。

用法，
## 服务端：
把服务端丢到服务器上，当然本机也能用，直接运行python server.py，就服务端就算启动完了。
X86的WIN系统和X86的ISTOREOS（Ｊ１９００）嵌入式linux系统，我试过了没什么问题。。
让服务端 非独占，后台运行，以及开机运行这些个基本的操作，问AI，让他引导就搞的定。。

至于缺库，按报错提示安装就可以了。能运行了之后退出来，把config.json的IP和端口，改成你自己的。

## 客户端：
同理，直接python main_client.py就行，缺库同理操作。
客户端的config.json，和服务端的配置文件，IP和端口，要一致。
然后，你自己随便打包个EXE就算能用了。

这玩意实现了，和QQ微信一样的托盘闪烁，我在GIT上找了快半年了，就找不到一个能实现的，就自己写了一个。
但是我只闪了图标，没加声音，也许以后会加吧，图标可以自己改，项目目录一眼就能看懂。


客户端 的单条删除和全部清除是能操作到数据库的，会抹掉本地和数据库里的消息。

仅单实例运行，防止重复运行。


simple_test.py，是个测试脚本，我自己用的，换一下IP地址，端口，就可以测试了。
里面的图片地址，自己换一下，上传的时候，图让我删了，直接行运行，我记得是不会报错，因为我记着我是按可以发空白消息写的。

就这样吧，这个测试的ｐｙ，收拾收拾，扔自己的游戏脚本里，就能实现发通知了。

主要场景就是脚本异常啊，游戏里出好东西了啊，人物躺了啊什么的特殊情况，就发个通知出来。

如果发图的话，其实也挺快的，毕竟也就是个游戏截图，但是如果有必要，就开个线程，单独发，不要影响到游戏脚本。


### 2025.8.18
优化一下客户端代码量，修正保存图片的路径，应为客户端的路径内。而不是在外面


#### 一个调用例子，从一个模块导入这段函数，在模块里把函数的IP填写为服务端的IP和商口，我偿试在调用处直接传参，但是失败了，所以只能在模块里填写，暂时我也不想知道为什么了，有空再研究，
#### 调用个截图函数，然后把这个图发出去，填上标题，内容，什么的，刚有试图片不在，会报错，所以尽量保证，这些参数调用的东西都存在，短期内我不一定有精力修复这些。。。
###  因为我这是真实的例子复制过来的，while套for，所以有一堆的状态变量，看的有些乱，各位自行测试的时候，可以仅保留发送的一套逻辑就行了。。。。

```
            dr.skip_war_other(dm)           #按ESC和跳过各种
            #向检测角色是否死亡的函数传递的状态变量
            #如果变量写在这里，那么每次for都会检查一下，也就是说如果角色再次死亡，那么会再次打印死亡信息！
            die_msg_printed = False
            die_true_msg_printed = False
            death_notification_sent = False    # 添加死亡通知发送状态变量

            dm.MoveTo(gc_x2, gc_y2)
            dm.Delay(3500)
    
            dm.KeyPress(118)        #F7 随便按2次
            dm.Delay(50)
            dm.KeyPress(118)
            dm.Delay(3310)
            
            dm.RightClick()         #随便按2次右键
            dm.Delay(50)
            dm.RightClick()
            dm.Delay(300)
            
            for i in range(130):        #攻击130次后，上面的代码使用一次F7魔法。
                if not stop_event.is_set() and win32gui.IsWindow(hwnd):

                    if not tip_printed:
                        print("法师攻击线程正在运行中...")
                        tip_printed = True

                    # 缩进太多次，注意这里起的缩进，只有在not字符正下方，能会在检查停止信号范围内！


                    die_msg_printed = dr.character_die(dm,stop_event,ocr_name,die_msg_printed)    # 调用dragonraja模块的character_die函数，检查角色是否处在战斗状态
                    die_true_msg_printed = dr.cha_true_die(dm,hwnd,ocr_name,die_true_msg_printed)    # 调用dragonraja模块的cha_true_die函数，检查角色是否真正死亡


                    if die_true_msg_printed and not death_notification_sent:
                        from utils.windows_setup import send_mixed_message

                        cha_die_cap_ret = dm.Capture(0,0,1366,768,"screen.bmp")
                        dm.Delay(200)


                        your_title = "角色真正死亡"    # 填写消息标题（可选，默认为"图文消息"）
                        your_text_content = "游戏角色已经飘了，查看详情里的图片，可以看到是不是被人攻击的，如果是被人物攻击的，那么截图里通常会保留被人攻击的人物的名字。"    # 填写你要发送的文字内容


                        your_image_path = r"D:\python_Scripts_32\jiayuan_guaji_pj_724_rebuild\screen.bmp"    # 填写你要发送的图片路径



                        # 调用函数发送消息
                        success = send_mixed_message(
                            image_path=your_image_path,
                            text_content=your_text_content,
                            title=your_title                          

                        )

                                                
                        if success:
                            print("✅ 消息发送成功！")
                            death_notification_sent = True    # 标记通知已发送


```
