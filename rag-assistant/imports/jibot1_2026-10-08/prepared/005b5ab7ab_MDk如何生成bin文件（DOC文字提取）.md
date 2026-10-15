# 4，STM32 IAP学习资料/MDk如何生成bin文件.doc

原始来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\4，STM32 IAP学习资料.zip!/4，STM32 IAP学习资料/MDk如何生成bin文件.doc

提取范围：正文和表格文字。原文中的图片需另行查看原文件。

在MDK中如何生成*.bin格式的文件  在Realview MDK的集成开发环境中，默认情况下可以生成*.axf格式的调试文件和*.hex格式的可执行文件。虽然这两个格式的文件非常有利于ULINK2仿真器的下载和调试，但是ADS的用户更习惯于使用*.bin格式的文件，甚至有些嵌入式软件开发者已经拥有了*.bin格式文件的调试或烧写工具。为了充分地利用现有的工具，同时发挥Realview MDK集成开发环境的优势，将*.axf格式文件或*.hex格式文件转换成*.bin格式的文件是十分自然的想法。本文将详细的探讨这种转换方法。在详细的介绍这种方法之前，先了解一下ARM公司的RVCT开发套件中的fromelf.exe转换工具是十分必要的，因为在Realview MDK中生成*.bin格式文件的工具正是它。fromelf.exe转换工具的语法格式如下：fromelf [options] input_file其中[options]包括的选项及详细描述见表一。表一 fromelf工具的选项及描述表格在掌握了fromelf转换工具的语法格式以后，下面将介绍它在Realview MDK中的使用方法：
1：要先能生产可执行文件（即配置Output）

aa为生成的可执行文件明，（即编译后会生成一个aa.axf的文件）生成的bin文件就是从这个文件生成的







2：从可执行文件生成.bin文件(即配置User)

C:\Keil\ARM\BIN40\fromelf.exe  --bin -o :命令表示从可执行文件生成bin文件
D:\1\out\33.bin   ：生产的bin文件的路径和文件名 
D:\1\out\aa.axf   ：可执行文件的路径和文件名

编译后即可生产33.bin文件（注意路径是可变的）
