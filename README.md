# AIOps2020预赛评测脚本

## 使用说明

运行`python3 judge.py demo`，目录中将生成如下两个样例文件

- `answer.json`，样例标准答案，包含每个故障的编号、网元、需要被定位的指标集合。其中，网络故障对应的指标为`null`。
- `result.json`，选手提交的答案，为每个故障确定可能根因的有序列表。

运行`python3 judge.py judge`将对两个文件进行评分。