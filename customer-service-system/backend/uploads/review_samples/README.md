# 评价晒图教学样例

这四张图片由内置 imagegen 工具生成，用于虚构电商评价和多模态课程演示，不是真实买家上传。样图随仓库提供，种子脚本直接使用这些文件；没有晒图的评价继续保持为空。

| 文件 | 对应场景 |
| --- | --- |
| shoe_glue-demo.jpg | 灰色网面跑鞋，鞋底与鞋面分离、开胶 |
| earphone_broken-demo.jpg | 黑色蓝牙耳机与充电仓，一只耳机外壳缝隙可见 |
| broken_box-demo.jpg | 保温杯、裂损杯盖、挤压变形的纸箱 |
| package_scratch-demo.jpg | 带明显划痕的耳机仓与破损包装 |

耳机是否有声音不能只靠图片判断，分析时应结合评价原文。

## 生成提示词

共同要求：`Use case: photorealistic-natural. Asset type: fictional teaching demo customer review photo for an ecommerce analysis course. Create one realistic square photo. Natural daylight, candid customer smartphone photo, no text, logos, watermark or collage.`

- shoe_glue：`Close-up of an unbranded light gray mesh running shoe on a wooden home floor. The white rubber outsole is visibly peeling away from the fabric upper along the front side, a clear wide gap revealing failed glue. Show the whole shoe with the separation sharply visible in foreground.`
- earphone_broken：`A pair of unbranded black true wireless in-ear earbuds next to their open charging case on a plain home desk. One earbud has a visibly separated casing seam exposing a small gap. No glowing graphics or symbolic sound icons. Physical product only; this photo cannot claim to prove a silent right earbud.`
- broken_box：`An unbranded stainless steel insulated travel bottle, a detached dark gray plastic screw lid with a large visible crack on its edge in the foreground, beside a dented and creased brown cardboard shipping box on a home desk. Defects easy to see.`
- package_scratch：`An unbranded dark gray wireless earbud charging case showing several conspicuous whitish scratches on the lid, beside a crushed brown cardboard package with torn edges and wrinkled paper packing on a home desk.`
