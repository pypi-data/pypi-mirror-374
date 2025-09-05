import ipywidgets as widgets
from IPython.display import display

def get_multiple_inputs(inputs_list:list):
    # 创建一个字典来存储输入的值
    input_storage = {}

    # 创建多个文本输入框
    text_inputs = []
    for i in inputs_list:
        text_inputs.append(widgets.Textarea(
            value=None,
            description=i,
            disabled=False
        ))

    # 创建一个提交按钮
    submit_button = widgets.Button(description="SUBMIT")

    # 定义一个回调函数来处理提交事件
    def on_submit(b):
        for text_input in text_inputs:
            param_name = text_input.description
            input_storage[param_name] = text_input.value if text_input.value.strip() else None
        print("Your inputs are:")
        for key, value in input_storage.items():
            print(f"{key}: {value}")
        # 清除输出和输入框，准备下一次输入
        for text_input in text_inputs:
            text_input.value = ''
        submit_button.description = "SUBMITTED"

    # 将回调函数绑定到提交按钮上
    submit_button.on_click(on_submit)

    # 显示文本输入框和提交按钮
    display(*text_inputs, submit_button)

    # 返回存储输入值的字典
    return input_storage