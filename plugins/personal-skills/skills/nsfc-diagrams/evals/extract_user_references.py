"""从项目提供的原图与documents渲染结果裁图；在源项目根目录运行。
源文件不属于技能依赖，仅复现参考库时需要。不会改写来源文件。
"""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil
R=Path.cwd();A=Path(__file__).resolve().parents[1]/'assets';T=R/'tmp/reference_review'
for p in ['references/mechanism','references/framework','details','original-vectors']:(A/p).mkdir(parents=True,exist_ok=True)
records=[]
def save(src,dest,box,source,locator,status='完整参考',use=''):
    im=Image.open(src);w,h=im.size
    bounds=[round(box[0]*w),round(box[1]*h),round(box[2]*w),round(box[3]*h)]
    im.crop(bounds).save(A/dest)
    records.append(dict(asset=dest,source=source,locator=locator,source_sha256=hashlib.sha256((R/source).read_bytes()).hexdigest(),crop_normalized=box,status=status,use=use))
for i in [1,2,3]:
    save(T/f'开放集-{i}.png',f'references/mechanism/open-set-{i}.png',(0,.14,1,.85 if i==2 else .69 if i==1 else .57),'开放集目标检测_侯竞夫.pptx',f'幻灯片{i}',use='对象、特征、分支与机制形状')
    shutil.copyfile(T/f'open_{i}_0.emf',A/f'original-vectors/open-set-{i}.emf')
    records.append(dict(asset=f'original-vectors/open-set-{i}.emf',source='开放集目标检测_侯竞夫.pptx',locator=f'幻灯片{i}唯一嵌入EMF',status='原始EMF矢量，未承诺逐元素可编辑'))
# Normalized bounds measured from original rendered pages, excluding prose/captions.
for fig,page,box in [(2,18,(.195,.48,.81,.884)),(3,20,(.151,.091,.865,.501)),(4,21,(.150,.371,.865,.678)),(8,33,(.150,.199,.86,.374)),(9,34,(.155,.188,.855,.407))]:
    folder='framework' if fig==2 else 'mechanism'
    save(T/f'document-render/page-{page}.png',f'references/{folder}/template-fig-{fig}.png',box,'模板.docx',f'PDF第{page}页；印刷页{page-1}；图{fig}',status='源文本异常，仅形状与连接参考' if fig==9 else '完整参考；保留源图水印',use='图形表达和排版，不复用研究结论')
save(T/'课题二.png','references/framework/topic-two.png',(0,.055,1,.957),'课题二技术路线图.pptx','幻灯片1',use='编号标题、分级字体、关系箭头及内部机制丰富度')
details=[('encoder','开放集-1.png',(.102,.17,.279,.447),'开放集目标检测_侯竞夫.pptx','幻灯片1：多模态编码器'),('clusters','开放集-1.png',(.296,.17,.47,.665),'开放集目标检测_侯竞夫.pptx','幻灯片1：聚类双视图'),('contrast-branches','开放集-2.png',(.632,.146,.97,.842),'开放集目标检测_侯竞夫.pptx','幻灯片2：两类对照分支'),('distribution-alignment','开放集-3.png',(.690,.243,.885,.501),'开放集目标检测_侯竞夫.pptx','幻灯片3：分布对齐'),('title-style','课题二.png',(.01,.059,.44,.18),'课题二技术路线图.pptx','幻灯片1：编号标题和摘要带'),('relation-arrows','课题二.png',(.439,.178,.505,.42),'课题二技术路线图.pptx','幻灯片1：前向/返回关系'),('internal-hierarchy','课题二.png',(.015,.708,.43,.94),'课题二技术路线图.pptx','幻灯片1：内部强调、辅助文字和具体对象')]
for name,file,box,src,loc in details:save(T/file,f'details/{name}.png',box,src,loc,use='局部参考裁图，不是可编辑组件')
for record in records:
    record['asset_sha256']=hashlib.sha256((A/record['asset']).read_bytes()).hexdigest()
    if 'source_sha256' not in record:record['source_sha256']=hashlib.sha256((R/record['source']).read_bytes()).hexdigest()
(A/'reference-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print('已保存',len(records),'条有来源的参考记录')

