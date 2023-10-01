# DataExtractor

> Author: qsdz
>
> Email: qingsiduzou@gmail.com

## 简介

DataExtractor 想成为一个可以从任意文件中提取各种数据的脚本，只需要撰写插件就可以通过调用不同的插件来提取数据。

现已有的插件有

- keyboard: 从键盘流量中提取键盘输入
- mice: 从鼠标流量中提取鼠标轨迹
- micelog: 从 `/dev/input/mice` 的鼠标日志中提取鼠标轨迹

- ...

目前支持的插件较少，插件内容在 `extensions` 包中。

> 使用 click 进行命令行脚本开发。

## 使用

可以通过 `--help` 参数获取帮助，目前来说帮助已经足够了解各参数的用处。

简单地测试实例

```bash
python dataextractor.py -f keyboard_test/example.pcap keyboard
```

输出

```
[-] Unkown hid-data: 01:00:00:00:00:00:00:00
[-] Unkown hid-data: 01:00:06:00:00:00:00:00
[+] Device ID: 2.1.1
[+] Raw: flag{pr355_0nwards_a2fee6e0}
[+] Content: flag{pr355_0nwards_a2fee6e0}
```



## 开发

### 愿景

目前想要开发的插件是文件格式提取，例如输入一个 BMP 文件，将其以字典格式（Json 格式）提取数据，并且可以自动化判断头进行解析。

可能的想法，通过 `-T` 参数控制输出格式（Json 或纯文本）。



### 指南

一个插件必须在 `extensions` 文件夹（包）内创建，其必须在以下代码的基础上进行修改

```python
import click

@click.command()
@click.pass_context
def parse(ctx: click.Context):
    ...
```

其中上下文 `ctx` 中的 `obj` 包含以下内容：

- filepath: `-f` 参数输入文件的完整路径
- filedir: 输入文件的完整目录
- filename: 输入文件的文件名
- filehash: 输入文件的哈希值
- tmpname: 临时文件的文件名
- tmppath: 临时文件的完整路径
- level: 输出信息的等级

可以通过上下文进行一些必要的处理。

同时可以从包内包含一些辅助函数，即

```python
from . import success_echo, fail_echo, debug_echo, set_level, call_outer
from .utils import unhexlify, hexlify
from .tsharkutils import get_layers
```

其中，所有插件的输出必须通过 `success_echo, fail_echo, debug_echo` 实现，其中对应成功输出、错误输出和调试输出。

可以通过 `set_level` 函数设置输出等级以控制输出信息。

而 `call_outer` 函数辅助调用其他程序并返回输出。

`unhexlify, hexlify` 帮助将 `01:02:03:04` 这样的十六进制字符串和 `b'\x01\x02\x03\x04'` 这样的字节流进行互相转换。

`get_layers` 帮助通过 tshark 获取过滤出来的所有 `layers`。

在这之上便可以通过 click 等库辅助编写插件。





