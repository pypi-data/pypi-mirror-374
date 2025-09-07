## 介绍

这是一个可为中小型 Python 项目提供配置管理的基类。

配置文件使用 YAML 格式，易读。

最简易的配置管理，就是单个文件里存放全部的配置，解析 YAML 后，直接用字典、列表去访问。但这样的缺点是没有代码补全，在配置有增删时也无法让程序静态分析，但更为不便的是没法复用一些相对固定的配置。

本库通过少量代码，和编程规范，解决上述问题：
1. 手动将程序所需的配置一一作为属性添加到数据类上，这样实现代码补全，方便静态分析
2. 提供解析配置文件的类方法，该方法接收单个配置文件路径，并从中得到其他配置文件路径，最终将这些配置合而为一，实现复用

合并配置的规则：
1. 配置文件中需要包含键值对 `other_configs_path: []`，里面放上其他配置文件路径。
2. `other_configs_path` 中靠后的配置，如果值是字符串、数字、布尔类型，会覆盖靠前的配置；如果值是列表类型，会追加到后面；如果值是字典类型，如果有重复字段，则根据值类型由前面规则决定，新字段会添加。
3. 当前配置文件会覆盖 `other_configs_path` 中合并后的配置。


## 用法

继承基类创建项目的配置类，基类中提供了一些有用的类方法。

```python
# config_handle.py
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from briefconf import BriefConfig

# 请自行更改环境变量的名称
configfile = os.getenv("PROJECT_CONFIG_FILE", default="config.yaml")
merged_config = os.getenv("PROJECT_MERGED_CONFIG", default="")  # 如果要查看合并后的配置，就通过此环境变量传递路径


@dataclass(frozen=True, slots=True)
class Config(BriefConfig):
    """所有配置参数都作为属性，列举在下面。通过类方法初始化配置实例，将配置的获取和配置参数分开放置，程序结构更加清晰。"""
    is_production: bool

    @classmethod
    def load(cls, config_path: str) -> Self:
        configs = cls._load_config(config_path)
        if merged_config:
            Path(merged_config).write_text(BriefConfig._dump(configs))

        return cls(
            is_production=configs["is_production"]
        )


config = Config.load(os.path.abspath(configfile))

__all__ = ["config"]

```

在其他文件中获得配置参数的值

```python
from config_handle import config

assert config.is_production
```

---

更具体的使用案例，可以查看 tests/config_handle.py


## 版本迭代

如果将来 BriefConfig 提供的类方法或行为与之前版本不兼容，会将旧版本保留在子模块中，这样升级后出现问题，只需要从子模块引入即可

```python
from briefconf import BriefConfig

class Config(BriefConfig):
    ...
```

从子模块中引入旧的版本

```python
from briefconf.v1 import BriefConfig

class Config(BriefConfig):
    ...
```
