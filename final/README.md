# AIOps2020复赛评测脚本

## 选手需要准备的内容

一个Docker镜像，其中包含了选手的程序和需要的环境。[example](example/)目录提供了Python样例程序，说明如何消费Kafka、输出答案、以及通过[Dockerfile](https://docs.docker.com/engine/reference/builder/)构建Docker镜像。

## 使用方式

1. 请将Docker镜像命名为`aiops`。
   - 复赛中，Docker镜像将运行在分发给选手的服务器上，统一的镜像命名可以方便挑战赛组织者统一启动选手镜像。
   - 如果使用Dockerfile，可以通过`docker build -t aiops example/`来构建生成名为`aiops`的镜像。
2. 启动镜像。
   - 启动的镜像实例称为_Docker容器_。
   - 通过命令`docker run --name aiops aiops`来启动镜像，其中，第一个`aiops`为启动的Docker容器的名字，第二个`aiops`为镜像的名字，还可以使用`-d`参数使Docker容器运行在后台。
   - **务必配置Docker镜像的入口[CMD](https://docs.docker.com/engine/reference/builder/#cmd)和/或[ENTRYPOINT](https://docs.docker.com/engine/reference/builder/#entrypoint)**。
3. 获得容器日志。
   - 通过命令`docker logs -t aiops > aiops.log`获得启动的Docker容器的标准输出，其中`-t`参数会在标准输出前添加时间戳。
4. 计算故障平均定位时间。
   - 执行`python judge.py answer.json aiops.log`进行评分，其中`answer.json`为标准答案。
   - `sample_answer.json`和`sample_result.log`分别提供了标准答案和容器输出的样例。
5. 为多个队伍打分。
   - 执行`python assemble.py --answer sample_answer.json --result-dir result --team-list team.csv`获得不同队伍的分数。
   - 使用`--score`参数选择不同的评分方式。

## Tips

- 注意需要**换行**和**刷新缓冲区**。
  - 不刷新缓冲区可能会使记录的提交时间严重滞后。
- 可以在[DockerHub](https://hub.docker.com/search?type=image)上获得镜像，例如
  - 额外启动[postgres](https://hub.docker.com/_/postgres)来提供数据库服务。
  - 以[python](https://hub.docker.com/_/python)为基础构建镜像而不必从[ubuntu](https://hub.docker.com/_/ubuntu)镜像开始。
