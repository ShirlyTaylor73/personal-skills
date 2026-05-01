--- Page 1 ---
https://robotics-transformer2.github.io
2023-8-1
RT-2: Vision-Language-Action Models Transfer
Web Knowledge to Robotic Control
AnthonyBrohan,NoahBrown,JusticeCarbajal,YevgenChebotar,XiChen,KrzysztofChoromanski,
TianliDing,DannyDriess,AvinavaDubey,ChelseaFinn,PeteFlorence,ChuyuanFu,
MontseGonzalezArenas,KeerthanaGopalakrishnan,KehangHan,KarolHausman,AlexanderHerzog,
JasmineHsu,BrianIchter,AlexIrpan,NikhilJoshi,RyanJulian,DmitryKalashnikov,YuhengKuang,
IsabelLeal,LisaLee,Tsang-WeiEdwardLee,SergeyLevine,YaoLu,HenrykMichalewski,IgorMordatch,
KarlPertsch,KanishkaRao,KristaReymann,MichaelRyoo,GreciaSalazar,PannagSanketi,
PierreSermanet,JaspiarSingh,AnikaitSingh,RaduSoricut,HuongTran,VincentVanhoucke,QuanVuong,
AyzaanWahid,StefanWelker,PaulWohlhart,JialinWu,FeiXia,TedXiao,PengXu,SichunXu,TianheYu,
andBriannaZitkovich
GoogleDeepMind.Authorslistedinalphabeticalorder,withcontributionslistedinAppendixA.
Westudyhowvision-languagemodelstrainedonInternet-scaledatacanbeincorporateddirectlyinto
end-to-endroboticcontroltoboostgeneralizationandenableemergentsemanticreasoning. Ourgoalis
toenableasingleend-to-endtrainedmodeltobothlearntomaprobotobservationstoactionsandenjoy
thebenefitsoflarge-scalepretrainingonlanguageandvision-languagedatafromtheweb. Tothisend,
weproposetoco-fine-tunestate-of-the-artvision-languagemodelsonbothrobotictrajectorydataand
Internet-scalevision-languagetasks,suchasvisualquestionanswering. Incontrasttootherapproaches,
weproposeasimple,generalrecipetoachievethisgoal: inordertofitbothnaturallanguageresponses
androboticactionsintothesameformat,weexpresstheactionsastexttokensandincorporatethem
directly into the training set of the model in the same way as natural language tokens. We refer to
suchcategoryofmodelsasvision-language-actionmodels(VLA)andinstantiateanexampleofsuch
amodel,whichwecallRT-2. Ourextensiveevaluation(6kevaluationtrials)showsthatourapproach
leadstoperformantroboticpoliciesandenablesRT-2toobtainarangeofemergentcapabilitiesfrom
Internet-scaletraining. Thisincludessignificantlyimprovedgeneralizationtonovelobjects,theability
tointerpretcommandsnotpresentintherobottrainingdata(suchasplacinganobjectontoaparticular
numberoricon),andtheabilitytoperformrudimentaryreasoninginresponsetousercommands(such
aspickingupthesmallestorlargestobject,ortheoneclosesttoanotherobject). Wefurthershowthat
incorporatingchainofthoughtreasoningallowsRT-2toperformmulti-stagesemanticreasoning,for
examplefiguringoutwhichobjecttopickupforuseasanimprovisedhammer(arock),orwhichtype
ofdrinkisbestsuitedforsomeonewhoistired(anenergydrink).
1. Introduction
High-capacity models pretrained on broad web-scale datasets provide an effective and powerful
platformforawiderangeofdownstreamtasks: largelanguagemodelscanenablenotonlyfluenttext
generation(Aniletal.,2023;Brohanetal.,2022;OpenAI,2023)butemergentproblem-solving(Cobbe
et al., 2021; Lewkowycz et al., 2022; Polu et al., 2022) and creative generation of prose (Brown
et al., 2020; OpenAI, 2023) and code (Chen et al., 2021), while vision-language models enable
open-vocabulary visual recognition (Kirillov et al., 2023; Minderer et al., 2022; Radford et al., 2021)
andcanevenmakecomplexinferencesaboutobject-agentinteractionsinimages(Alayracetal.,2022;
Chenetal.,2023a,b;Driessetal.,2023;Haoetal.,2022;Huangetal.,2023;Wangetal.,2022). Such
semantic reasoning, problem solving, and visual interpretation capabilities would be tremendously
useful for generalist robots that must perform a variety of tasks in real-world environments. However,
Correspondingauthor(s):chebotar@google.com,tianheyu@google.com,karolhausman@google.com
© 2023GoogleDeepMind.Allrightsreserved
3202
luJ
82
]OR.sc[
1v81851.7032:viXra

--- Page 2 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
Internet-Scale VQA + Robot Action Data Vision-Language-Action Models for Robot Control Closed-Loop
Robot Control
Q: What is happening Q: What should the robot RT-2
in the image? do to <task>? A: … Large Language Model
A: 311 423 170 55 244
A grey donkey walks
down the street.
Put the strawberry
Q: Que puis-je faire avec ViT into the correct bowl
ces objets?
A: 3455 1144 189 25673
Faire cuire un gâteau.
ΔT = [0.1, -0.2, 0]
Q: What should the robot A: 132 114 128 5 25 156 De-Tokenize ΔR = [10∘ , 25∘ , -7∘ ] Pick the nearly falling bag
do to <task>? Robot Action
A: 132 114 128 5 25 156
Δ Translation = [0.1, -0.2, 0]
ΔRotation = [10∘ , 25 ∘, -7 ∘ ] Co-Fine-Tune Deploy
Pick object that is different
Figure1|RT-2overview:werepresentrobotactionsasanotherlanguage,whichcanbecastintotexttokensand
trainedtogetherwithInternet-scalevision-languagedatasets. Duringinference,thetexttokensarede-tokenized
into robot actions, enabling closed loop control. This allows us to leverage the backbone and pretraining
of vision-language models in learning robotic policies, transferring some of their generalization, semantic
understanding,andreasoningtoroboticcontrol. WedemonstrateexamplesofRT-2executionontheproject
website: robotics-transformer2.github.io.
it is unclear how robots should acquire such capabilities. While a brute force approach might entail
collectingmillionsofroboticinteractiontrials,themostcapablelanguageandvision-languagemodels
are trained on billions of tokens and images from the web (Alayrac et al., 2022; Chen et al., 2023a,b;
Huang et al., 2023) – an amount unlikely to be matched with robot data in the near future. On the
other hand, directly applying such models to robotic tasks is also difficult: such models reason about
semantics, labels, and textual prompts, whereas robots require grounded low-level actions, such
as Cartesian end-effector commands. While a number of recent works have sought to incorporate
language models (LLMs) and vision-language models (VLMs) into robotics (Ahn et al., 2022; Driess
etal.,2023;Vempralaetal.,2023),suchmethodsgenerallyaddressonlythe“higherlevel”aspectsof
robotic planning, essentially taking the role of a state machine that interprets commands and parses
them into individual primitives (such as picking and placing objects), which are then executed by
separate low-level controllers that themselves do not benefit from the rich semantic knowledge of
Internet-scale models during training. Therefore, in this paper we ask: can large pretrained vision-
language models be integrated directly into low-level robotic control to boost generalization and
enable emergent semantic reasoning?
To this end, we explore an approach that is both simple and surprisingly effective: we directly
train vision-language models designed for open-vocabulary visual question answering and visual
dialogue to output low-level robot actions, along with solving other Internet-scale vision-language
tasks. Although such models are typically trained to produce natural language tokens, we can train
them on robotic trajectories by tokenizing the actions into text tokens and creating “multimodal
sentences”(Driessetal.,2023)that“respond”toroboticinstructionspairedwithcameraobservations
by producing corresponding actions. In this way, vision-language models can be directly trained to
actasinstructionfollowingroboticpolicies. Thissimpleapproachisincontrastwithprioralternatives
for incorporating VLMs into robot policies (Shridhar et al., 2022a) or designing new vision-language-
action architectures from scratch (Reed et al., 2022): instead, pre-existing vision-language models,
with already-amortized significant compute investment, are trained without any new parameters to
output text-encoded actions. We refer to this category of models as vision-language-action (VLA)
models. We instantiate VLA models by building on the protocol proposed for RT-1 (Brohan et al.,
2022), using a similar dataset, but expanding the model to use a large vision-language backbone.
Hence we refer to our model as RT-2 (Robotics Transformer 2). We provide an overview in Figure 1.
2

--- Page 3 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
We observe that robotic policies derived from such vision-language models exhibit a range of
remarkable capabilities, combining the physical motions learned from the robot data with the ability
to interpret images and text learned from web data into a single model. Besides the expected benefit
of dramatically improving generalization to novel objects and semantically varied instructions, we
observe a number of emergent capabilities. While the model’s physical skills are still limited to the
distribution of skills seen in the robot data, the model acquires the ability to deploy those skills in
new ways by interpreting images and language commands using knowledge gleaned from the web.
Some example highlights are shown in Figure 2. The model is able to re-purpose pick and place
skills learned from robot data to place objects near semantically indicated locations, such as specific
numbersoricons,despitethosecuesnotbeingpresentintherobotdata. Themodelcanalsointerpret
relations between objects to determine which object to pick and where to place it, despite no such
relations being provided in the robot demonstrations. Furthermore, if we augment the command
with chain of thought prompting, the model is able to make even more complex semantic inferences,
such as figuring out which object to pick up for use as an improvised hammer (a rock), or which type
of drink is best suited for someone who is tired (an energy drink).
Our main contribution is RT-2, a family of models derived from fine-tuning large vision-language
models trained on web-scale data to directly act as generalizable and semantically aware robotic
policies. Our experiments investigate models with up to 55B parameters trained on Internet data
and instruction-annotated robotic trajectories from previous work (Brohan et al., 2022). Over the
courseof6kroboticevaluations,weshowthatRT-2enablesignificantimprovementstogeneralization
over objects, scenes, and instructions, and exhibit a breadth of emergent capabilities inherited from
web-scale vision-language pretraining.
2. Related Work
Vision-language models. There are several categories of Vision-Language Models (VLMs) (Gan et al.,
2022), with perhaps two most relevant: (1) representation-learning models, e.g. CLIP (Radford
et al., 2021), which learn common embeddings for both modalities, and (2) visual language models
of the form {vision,text} → {text} which learn to take vision and language as input and provide
free-form text. Both categories have been used to provide pretraining for a wide variety of applied
to downstream applications such as object classification (Radford et al., 2021), detection (Gu et al.,
2021), and segmentation (Ghiasi et al., 2021). In this work, we focus on the latter category (Alayrac
et al., 2022; Chen et al., 2023a,b; Driess et al., 2023; Hao et al., 2022; Li et al., 2023, 2019; Lu
et al., 2019). These models are generally trained on many different tasks, such as image captioning,
vision-question answering (VQA), and general language tasks on multiple datasets at the same time.
While prior works study VLMs for a wide range of problems and settings including in robotics, our
focus is on how the capabilities of VLMs can be extended to robotics closed-loop control by endowing
themwiththeabilitytopredictrobotactions,thusleveragingtheknowledgealreadypresentinVLMs
to enable new levels of generalization.
Generalization in robot learning. Developing robotic controllers that can broadly succeed in a
variety of scenarios is a long-standing goal in robotics research (Kaelbling, 2020; Smith and Coles,
1973). A promising approach for enabling generalization in robotic manipulation is by learning from
large anddiverse datasets(Dasari etal.,2019;Levineetal.,2018; Pintoand Gupta,2016). Bydoing
so, prior methods have demonstrated how robots can generalize to novel object instances (Finn and
Levine,2017;Levineetal.,2018;Mahleretal.,2017;PintoandGupta,2016;Youngetal.,2021),to
tasks involving novel combinations of objects and skills (Dasari and Gupta, 2021; Finn et al., 2017;
James et al., 2018; Jang et al., 2021; Yu et al., 2018), to new goals or language instructions (Jang
et al., 2021; Jiang et al., 2022; Liu et al., 2022; Mees et al., 2022; Nair et al., 2022a; Pong et al.,
3

--- Page 4 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
2019), to tasks with novel semantic object categories (Shridhar et al., 2021; Stone et al., 2023), and
tounseenenvironments(Cuietal.,2022;Duetal.,2023a;Hansenetal.,2020). Unlikemostofthese
prior works, we aim to develop and study a single model that can generalize to unseen conditions
along all of these axes. A key ingredient of our approach is to leverage pre-trained models that have
been exposed to data that is much broader than the data seen by the robot.
Pre-training for robotic manipulation. Pre-training has a long history in robotic learning. Most
works focus on pre-trained visual representations that can be used to initialize the encoder of the
robot’s camera observations, either via supervised ImageNet classification (Shah and Kumar, 2021),
data augmentation (Kostrikov et al., 2020; Laskin et al., 2020a,b; Pari et al., 2021) or objectives
that are tailored towards robotic control (Karamcheti et al., 2023; Ma et al., 2022; Majumdar et al.,
2023b; Nair et al., 2022b; Xiao et al., 2022b). Other works have incorporated pre-trained language
models, often either as an instruction encoder (Brohan et al., 2022; Hill et al., 2020; Jang et al.,
2021; Jiang et al., 2022; Lynch and Sermanet, 2020; Nair et al., 2022a; Shridhar et al., 2022b) or
for high-level planning (Ahn et al., 2022; Driess et al., 2023; Huang et al., 2022; Mu et al., 2023;
Singh et al., 2023; Wu et al., 2023). Rather than using pre-training vision models or pre-trained
language models, we specifically consider the use of pre-trained vision-language models (VLMs),
which provide rich, grounded knowledge about the world. Prior works have studied the use of VLMs
for robotics (Driess et al., 2023; Du et al., 2023b; Gadre et al., 2022; Karamcheti et al., 2023; Shah
et al., 2023; Shridhar et al., 2021; Stone et al., 2023), and form part of the inspiration for this
work. Thesepriorapproaches useVLMs forvisualstaterepresentations(Karamchetietal.,2023), for
identifyingobjects(Gadreetal.,2022;Stoneetal.,2023),forhigh-levelplanning(Driessetal.,2023),
or for providing supervision or success detection (Du et al., 2023b; Ma et al., 2023; Sumers et al.,
2023; Xiao et al., 2022a; Zhang et al., 2023). While CLIPort (Shridhar et al., 2021) and MOO (Stone
et al., 2023) integrate pre-trained VLMs into end-to-end visuomotor manipulation policies, both
incorporate significant structure into the policy that limits their applicability. Notably, our work does
notrelyonarestricted2Dactionspaceanddoesnotrequireacalibratedcamera. Moreover,acritical
distinction is that, unlike these works, we leverage VLMs that generate language, and the unified
output space of our formulation enables model weights to be entirely shared across language and
action tasks, without introducing action-only model layer components.
3. Vision-Language-Action Models
In this section, we present our model family and the design choices for enabling training VLMs to
directly perform closed-loop robot control. First, we describe the general architecture of our models
and how they can be derived from models that are commonly used for vision-language tasks. Then,
we introduce the recipe and challenges of fine-tuning large VLMs that are pre-trained on web-scale
data to directly output robot actions, becoming VLA models. Finally, we describe how to make these
modelspracticalforrobottasks,addressingchallengeswithmodelsizeandinferencespeedtoenable
real-time control.
3.1. Pre-Trained Vision-Language Models
The vision-language models (Chen et al., 2023a; Driess et al., 2023) that we build on in this work
take as input one or more images and produce a sequence of tokens, which conventionally represents
natural language text. Such models can perform a wide range of visual interpretation and reasoning
tasks, from inferring the composition of an image to answering questions about individual objects
and their relations to other objects (Alayrac et al., 2022; Chen et al., 2023a; Driess et al., 2023;
Huang et al., 2023). Representing the knowledge necessary to perform such a wide range of tasks
4

--- Page 5 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
requires large models and web-scale datasets. In this work, we adapt two previously proposed VLMs
to act as VLA models: PaLI-X (Chen et al., 2023a) and PaLM-E (Driess et al., 2023). We will refer
to vision-language-action versions of these models as RT-2-PaLI-X and RT-2-PaLM-E. We leverage
instantiations of these models that range in size from billions to tens of billions of parameters. We
provide a detailed description of the architecture of these two models in Appendix D.
Figure 2 | RT-2 is able to generalize to a variety of real-world situations that require reasoning, symbol
understanding,andhumanrecognition. WestudythesechallengingscenariosindetailinSection4.
3.2. Robot-Action Fine-tuning
To enable vision-language models to control a robot, they must be trained to output actions. We
take a direct approach to this problem, representing actions as tokens in the model’s output, which
are treated in the same way as language tokens. We base our action encoding on the discretization
proposed by Brohan et al. (2022) for the RT-1 model. The action space consists of 6-DoF positional
and rotational displacement of the robot end-effector, as well as the level of extension of the robot
gripper and a special discrete command for terminating the episode, which should be triggered by
the policy to signal successful completion. The continuous dimensions (all dimensions except for
the discrete termination command) are discretized into 256 bins uniformly. Thus, the robot action
can be represented using ordinals of the discrete bins as 8 integer numbers. In order to use these
discretized actions to finetune a vision-language into a vision-language-action model, we need to
associate tokens from the model’s existing tokenization with the discrete action bins. This requires
5

--- Page 6 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
reserving 256 tokens to serve as action tokens. Which tokens to choose depends on the particular
tokenization used by each VLM, which we discuss later in this section. In order to define a target
for VLM fine-tuning we convert the action vector into a single string by simply concatenating action
tokens for each dimension with a space character:
“terminate Δpos Δpos Δpos Δrot Δrot Δrot gripper_extension”.
𝑥 𝑦 𝑧 𝑥 𝑦 𝑧
A possible instantiation of such a target could be: “1 128 91 241 5 101 127”. The two VLMs that
we finetune in our experiments, PaLI-X (Chen et al., 2023a) and PaLM-E (Driess et al., 2023), use
different tokenizations. For PaLI-X, integers up to 1000 each have a unique token, so we simply
associate the action bins to the token representing the corresponding integer. For the PaLM-E model,
which does not provide this convenient representation of numbers, we simply overwrite the 256 least
frequently used tokens to represent the action vocabulary. It is worth noting that training VLMs to
override existing tokens with action tokens is a form of symbol tuning (Wei et al., 2023), which has
been shown to work well for VLMs in prior work.
Taking the action representation described above, we convert our robot data to be suitable for
VLM model fine-tuning, where our inputs include robot camera image and textual task description
(usingstandardVQAformat“Q:whatactionshouldtherobottaketo[taskinstruction]? A:”),andour
output is formatted as a string of numbers/least frequently used tokens representing a robot action.
Co-Fine-Tuning. As we will show in our experiments, a key technical detail of the training recipe
that improves robot performance is co-fine-tuning robotics data with the original web data instead of
naïvefinetuningonrobotdataonly. Wenoticethatco-fine-tuningleadstomoregeneralizablepolicies
sincethepoliciesareexposedtobothabstractvisualconceptsfromwebscaledataandlowlevelrobot
actions during fine-tuning, instead of just robot actions. During co-fine-tuning we balance the ratios
of robot and web data in each training batch by increasing the sampling weight on the robot dataset.
Output Constraint. One important distinction between RT-2 and standard VLMs is that RT-2
is required to output valid action tokens for execution on the real robot. Thus, to ensure that RT-2
outputs valid action tokens during decoding, we constrain its output vocabulary via only sampling
valid action tokens when the model is prompted with a robot-action task, whereas the model is still
allowed to output the full range of natural language tokens on standard vision-language tasks.
3.3. Real-Time Inference
The size of modern VLMs can reach tens or hundreds of billions of parameters (Chen et al., 2023a;
Driess et al., 2023). The largest model trained in this work uses 55B parameters. It is infeasible to
directlyrunsuchmodelsonthestandarddesktop-stylemachinesoron-robotGPUscommonlyusedfor
real-time robot control. To the best of our knowledge, our model is the largest ever, by over an order
ofmagnitude,usedfordirectclosed-looproboticcontrol,andthereforerequiresanewsetofsolutions
to enable efficient real-time inference. We develop a protocol that allows us to run RT-2 models on
robots by deploying them in a multi-TPU cloud service and querying this service over the network.
Withthissolution,wecanachieveasuitablefrequencyofcontrolandalsoservemultiplerobotsusing
the same cloud service. The largest model we evaluated, the 55B parameter RT-2-PaLI-X-55B model,
can run at a frequency of 1-3 Hz. The smaller version of that model, consisting of 5B parameters, can
run at a frequency of around 5 Hz.
4. Experiments
Our experiments focus on real-world generalization and emergent capabilities of RT-2 and aim to
answer the following questions:
6

--- Page 7 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
1. How does RT-2 perform on seen tasks and more importantly, generalize over new objects,
backgrounds, and environments?
2. Can we observe and measure any emergent capabilities of RT-2?
3. How does the generalization vary with parameter count and other design decisions?
4. Can RT-2 exhibit signs of chain-of-thought reasoning similarly to vision-language models?
We evaluate our approach and several baselines with about 6,000 evaluation trajectories in a variety
of conditions, which we describe in the following sections. Unless specified otherwise, we use a
7DoF mobile manipulator with the action space described in Sec. 3.2. We also demonstrate examples
of RT-2 execution on the project website: robotics-transformer2.github.io. We train two
specific instantiations of RT-2 that leverage pre-trained VLMs: (1) RT-2-PaLI-X is built from 5B and
55B PaLI-X (Chen et al., 2023a), and (2) RT-2-PaLM-E is built from 12B PaLM-E (Driess et al., 2023).
For training, we leverage the original web scale data from Chen et al. (2023a) and Driess et al.
(2023), which consists of visual question answering, captioning, and unstructured interwoven image
and text examples. We combine it with the robot demonstration data from Brohan et al. (2022),
which was collected with 13 robots over 17 months in an office kitchen environment. Each robot
demonstration trajectory is annotated with a natural language instruction that describes the task
performed,consistingofaverbdescribingtheskill(e.g.,“pick”,”open”,“placeinto”)andoneormore
nouns describing the objects manipulated (e.g., “7up can”, “drawer”, “napkin”) (see Appendix B for
moredetailsontheuseddatasets). ForallRT-2trainingrunsweadoptthehyperparametersfromthe
original PaLI-X (Chen et al., 2023a) and PaLM-E (Driess et al., 2023) papers, including learning rate
schedules and regularizations. More training details can be found in Appendix E.
Baselines. We compare our method to multiple state-of-the-art baselines that challenge different
aspects of our method. All of the baselines use the exact same robotic data. To compare against a
state-of-the-art policy, we use RT-1 (Brohan et al., 2022), a 35M parameter transformer-based model.
Tocompareagainststate-of-the-artpretrainedrepresentations,weuseVC-1(Majumdaretal.,2023a)
and R3M (Nair et al., 2022b), with policies implemented by training an RT-1 backbone to take their
representationsasinput. TocompareagainstotherarchitecturesforusingVLMs,weuseMOO(Stone
et al., 2023), which uses a VLM to create an additional image channel for a semantic map, which is
then fed into an RT-1 backbone. More information is provided in Appendix C.
4.1. How does RT-2 perform on seen tasks and more importantly, generalize over new objects,
backgrounds, and environments?
(a) Unseen Objects (b) Unseen Backgrounds (c) Unseen Environments
Figure3 | ExamplegeneralizationscenariosusedforevaluationinFigures4and6bandTables4and6.
To evaluate in-distribution performance as well as generalization capabilities, we compare the
RT-2-PaLI-X and RT-2-PaLM-E models to the four baselines listed in the previous sections. For the
seen tasks category, we use the same suite of seen instructions as in RT-1 (Brohan et al., 2022), which
include over 200 tasks in this evaluation: 36 for picking objects, 35 for knocking objects, 35 for
placing things upright, 48 for moving objects, 18 for opening and closing various drawers, and 36 for
pickingoutofandplacingobjectsintodrawers. Note,however,thatthese“in-distribution”evaluations
still vary the placement of objects and factors such as time of day and robot position, requiring the
skills to generalize to realistic variability in the environment.
7

--- Page 8 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
Figure3showsexamplegeneralizationevaluations,whicharesplitintounseencategories(objects,
backgroundsandenvironments),andareadditionallysplitintoeasyandhardcases. Forunseenobjects,
hard cases include harder-to-grasp and more unique objects (such as toys). For unseen backgrounds,
hardcasesincludemorevariedbackgroundsandnovelobjects. Lastly,forunseenenvironments,hard
cases correspond to a more visually distinct office desk environment with monitors and accessories,
whiletheeasierenvironmentisakitchensink. Theseevaluationsconsistsofover280tasksthatfocus
primarily on pick and placing skills in many diverse scenarios. The list of instructions for unseen
categories is specified in Appendix F.2.
Figure4 | OverallperformanceoftwoinstantiationsofRT-2andbaselinesacrossseentrainingtasksaswellas
unseenevaluationsmeasuringgeneralizationtonovelobjects,novelbackgrounds,andnovelenvironments.
AppendixTable4detailsthefullresults.
The evaluation results are shown in Figure 4 and Appendix Table 4. The performance on seen
tasks is similar between the RT-2 models and RT-1, with other baselines attaining a lower success
rate. The difference between the RT-2 models and the baseline is most pronounced in the various
generalization experiments, suggesting that the strength of vision-language-action models lies in
transferring more generalizable visual and semantic concepts from their Internet-scale pretraining
data. Here, on average, both instantiations of RT-2 perform similarly, resulting in ∼2x improvement
over the next two baselines, RT-1 and MOO, and ∼6x better than the other baselines. The PaLM-E
version of RT-2 seems to perform better than the RT-2-PaLI-X in harder versions of generalization
scenarios while under-performing on easier ones, resulting in a similar average performance.
Open Source Language Table Benchmark. To provide an additional point of comparison using
open-source baselines and environments, we leverage the open-source Language-Table simulation
environmentfromLynchetal.(2022). Weco-fine-tuneasmallerPaLI3Bmodelonseveralprediction
tasks, including in-domain VQA tasks, for the Language-Table dataset, and evaluate the resulting
policy in simulation. For the action prediction task, we discretize and encode actions as text in the
format“X Y”,whereXandYrangebetween{-10,-9,...,+9,+10},andrepresentdelta2Dcartesian
setpointsoftheendeffector. Duetoitsreducedsize,theresultingmodelcanruninferenceatasimilar
rate(5Hz)astheotherbaselines. TheresultsofthisexperimentarepresentedinTable1. Weobserve
a significant performance boost when using our model compared to the baselines, indicating that the
VLM-based pre-training together with the expressiveness of the large PaLI model can be beneficial in
other scenarios, in this case, simulation with a different robot. We also show qualitative real-world
out-of-distribution behaviors behaviors in Figure 5, demonstrating novel pushing tasks and targeting
objects not before seen in this environment. More details about the Language Table experiments can
be found in Appendix B and D.
4.2. Can we observe and measure any emergent capabilities of RT-2?
Inadditiontoevaluatingthegeneralizationcapabilitiesofvision-language-actionmodels,wealsoaim
to evaluate the degree to which such models can enable new capabilities beyond those demonstrated
8

--- Page 9 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
Model Language-Table
BC-Zero(Jangetal.,2021) 72±3
RT-1(Brohanetal.,2022) 74±13
LAVA(Lynchetal.,2022) 77±4
RT-2-PaLI-3B(ours) 90±10
Figure 5 | Real-world out-of-distribution behaviors in the Table 1 | Performance on the simulated
LanguageTableenvironment. IdenticalRT-2-PaLI-3Bmodel Language-Table tasks (Lynch and Ser-
checkpointisusedasinTab.1. manet,2020).
intherobotdatabytransferringknowledgefromtheweb. Werefertosuchcapabilitiesasemergent,in
the sense that they emerge by transferring Internet-scale pretraining. We do not expect such transfer
to enable new robotic motions, but we do expect semantic and visual concepts, including relations
andnouns,totransfereffectively, evenincaseswherethoseconceptswerenotseenintherobotdata.
Qualitative Evaluations. First, we experiment with our RT-2-PaLI-X model to determine various
emergent capabilities transferred from vision-language concepts. We demonstrate some examples of
such interactions in Figure 2. We find through our explorations that RT-2 inherits novel capabilities
in terms of semantic understanding and basic reasoning in the context of the scene. For example
accomplishing the task “put strawberry into the correct bowl” requires a nuanced understanding of
not only what a strawberry and bowl are, but also reasoning in the context the scene to know the
strawberry should go with the like fruits. For the task “pick up the bag about to fall off the table,”
RT-2 demonstrates physical understanding to disambiguate between two bags and recognize the
precariously placed object. All the interactions tested in these scenarios have never been seen in the
robot data, which points to the transfer of semantic knowledge from vision-language data.
Quantitative Evaluations. Toquantifytheseemergentcapabilities,wetakethetoptwobaselines
fromthepreviousevaluations,RT-1andVC-1,andcomparethemagainstourtwomodels: RT-2-PaLI-X
and RT-2-PaLM-E. To reduce the variance of these experiment, we evaluate all of the methods using
the A/B testing framework (Fisher, 1936), where all four models are evaluated one after another in
the exact same conditions.
We’ split the emergent capabilities of RT-2 into three categories covering axes of reasoning and
semantic understanding (with examples of each shown in Appendix Figure 8). The first we term
symbol understanding, which explicitly tests whether the RT-2 policy transfers semantic knowledge
from vision-language pretraining that was not present in any of the robot data. Example instructions
in this category are “move apple to 3” or “push coke can on top of heart”. The second category we
termreasoning,whichdemonstratestheabilitytoapplyvariousaspectsofreasoningoftheunderlying
VLMtocontroltasks. Thesetasksrequirevisualreasoning(“movetheappletocupwithsamecolor”),
math (“move X near the sum of two plus one”), and multilingual understanding (“mueve la manzana
al vaso verde”). We refer to the last category as human recognition tasks, which include tasks such as
“move the coke can to the person with glasses”, to demonstrate human-centric understanding and
recognition. The full list of instructions used for this evaluation is specified in Appendix F.2.
WepresenttheresultsofthisexperimentinFigure6awithallthenumericalresultsinAppendixH.2.
We observe that our VLA models significantly outperform the baselines across all categories, with
our best RT-2-PaLI-X model achieving more than 3x average success rate over the next best baseline
(RT-1). WealsonotethatwhilethelargerPaLI-X-basedmodelresultsinbettersymbolunderstanding,
reasoning and person recognition performance on average, the smaller PaLM-E-based model has
an edge on tasks that involve math reasoning. We attribute this interesting result to the different
pre-trainingmixtureusedinPaLM-E,whichresultsinamodelthatismorecapableatmathcalculation
than the mostly visually pre-trained PaLI-X.
9

--- Page 10 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
(a)Performancecomparisononvariousemergentskillevalu-(b)AblationsofRT-2-PaLI-Xshowcasingtheimpactofparam-
ations(Figure8)betweenRT-2andtwobaselines. etercountandtrainingstrategyongeneralization.
Figure6 | QuantitativeperformanceofRT-2across(6a)emergentskillsand(6b)sizeandtrainingablations.
AppendixTables5and6detailthefullnumericalresults.
4.3. How does the generalization vary with parameter count and other design decisions?
For this comparison, we use RT-2-PaLI-X model because of its flexibility in terms of the model size
(duetothenatureofPaLM-E,RT-2-PaLM-EisrestrictedtoonlycertainsizesofPaLMandViTmodels).
In particular, we compare two different model sizes, 5B and 55B, as well as three different training
routines: training a model from scratch, without using any weights from the VLM pre-training;
fine-tuning a pre-trained model using robot action data only; and co-fine-tuning (co-training with
fine-tuning), the primary method used in this work where we use both the original VLM training
data as well as robotic data for VLM fine-tuning. Since we are mostly interested in the generalization
aspects of these models, we remove the seen tasks evaluation from this set of experiments.
The results of the ablations are presented in Figure 6b and Appendix Table 6. First, we observe
that training a very large model from scratch results in a very poor performance even for the 5B
model. Given this result, we decide to skip the evaluation of an even bigger 55B PaLI-X model when
trained from scratch. Second, we notice that co-fine-tuning a model (regardless of its size) results in
a better generalization performance than simply fine-tuning it with robotic data. We attribute this to
the fact that keeping the original data around the fine-tuning part of training, allows the model to
notforgetitspreviousconceptslearnedduringtheVLMtraining. Lastly,somewhatunsurprisingly,we
notice that the increased size of the model results in a better generalization performance.
4.4. Can RT-2 exhibit signs of chain-of-thought reasoning similarly to vision-language models?
Inspiredbythechain-of-thoughtpromptingmethodinLLMs(Weietal.,2022),wefine-tuneavariant
of RT-2 with PaLM-E for just a few hundred gradient steps to increase its capability of utilizing
language and actions jointly with the hope that it will elicit a more sophisticated reasoning behavior.
We augment the data to include an additional “Plan” step, which describes the purpose of the action
that the robot is about to take in natural language first, which is then followed by the actual action
tokens, e.g. “Instruction: I’m hungry. Plan: pick rxbar chocolate. Action: 1 128 124 136 121 158 111
255.” This data augmentation scheme acts as a bridge between VQA datasets (visual reasoning) and
manipulation datasets (generating actions).
We qualitatively observe that RT-2 with chain-of-thought reasoning is able to answer more so-
phisticated commands due to the fact that it is given a place to plan its actions in natural language
first. This is a promising direction that provides some initial evidence that using LLMs or VLMs as
planners(Ahnetal.,2022;Driessetal.,2023)canbecombinedwithlow-levelpoliciesinasingleVLA
model. Rollouts of RT-2 with chain-of-thought reasoning are shown in Figure 7 and in Appendix I.
10

--- Page 11 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
Prompt: Prompt: Prompt: Prompt:
Given <img> Instruction: Given <img> Instruction: Given <img> Instruction: Given <img> Instruction:
Bring me a drink. Move all the objects Pick the object that is Move the green objects
Prediction: together. different from all other together.
Plan: pick 7up can. Prediction: objects Prediction:
Action: 1 143 129 123 145 Plan: move green can near Prediction: Plan: move green can near
114 115 127 green rice chip bag. Plan: pick rxbar green rice chip bag.
Action: 1 128 126 127 135 chocolate. Action: 1 128 Action: 1 130 129 121 131
123 119 127 129 125 131 125 128 127 127 128 127
Prompt:
Given <img> I need to
hammer a nail, what
object from the scene
might be useful?
Prediction:
Rocks. Action: 1 129 138
122 132 135 106 127
Figure7 | RolloutsofRT-2withchain-of-thoughtreasoning,whereRT-2generatesbothaplanandanaction.
5. Limitations
Even though RT-2 exhibits promising generalization properties, there are multiple limitations of this
approach. First,althoughweshowthatincludingweb-scalepretrainingviaVLMsboostsgeneralization
over semantic and visual concepts, the robot does not acquire any ability to perform new motions
by virtue of including this additional experience. The model’s physical skills are still limited to the
distribution of skills seen in the robot data (see Appendix G), but it learns to deploy those skills in
new ways. We believe this is a result of the dataset not being varied enough along the axes of skills.
An exciting direction for future work is to study how new skills could be acquired through new data
collection paradigms such as videos of humans.
Second, although we showed we could run large VLA models in real time, the computation cost
of these models is high, and as these methods are applied to settings that demand high-frequency
control,real-timeinferencemaybecomeamajorbottleneck. Anexcitingdirectionforfutureresearch
is to explore quantization and distillation techniques that might enable such models to run at higher
ratesoronlower-costhardware. Thisisalsoconnectedtoanothercurrentlimitationinthatthereare
onlyasmallnumberofgenerallyavailableVLMmodelsthatcanbeusedtocreateRT-2. Wehopethat
more open-sourced models will become available (e.g. https://llava-vl.github.io/) and the
proprietary ones will open up their fine-tuning APIs, which is a sufficient requirement to build VLA
models.
6. Conclusions
In this paper, we described how vision-language-action (VLA) models could be trained by combining
vision-language model (VLM) pretraining with robotic data. We then presented two instantiations of
VLAs based on PaLM-E and PaLI-X, which we call RT-2-PaLM-E and RT-2-PaLI-X. These models are co-
fine-tuned with robotic trajectory data to output robot actions, which are represented as text tokens.
We showed that our approach results in very performant robotic policies and, more importantly,
leads to a significantly better generalization performance and emergent capabilities inherited from
11

--- Page 12 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
web-scale vision-language pretraining. We believe that this simple and general approach shows a
promise of robotics directly benefiting from better vision-language models, which puts the field of
robot learning in a strategic position to further improve with advancements in other fields.
Acknowledgments
WewouldliketoacknowledgeFredAlcober,JodiLynnAndres,CarolinaParada,JosephDabis,Rochelle
Dela Cruz, Jessica Gomez, Gavin Gonzalez, John Guilyard, Tomas Jackson, Jie Tan, Scott Lehrer, Dee
M, Utsav Malla, Sarah Nguyen, Jane Park, Emily Perez, Elio Prado, Jornell Quiambao, Clayton Tan,
Jodexty Therlonge, Eleanor Tomlinson, Wenxuan Zhou, and the greater Google DeepMind team for
their feedback and contributions.
12

--- Page 13 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
References
M.Ahn,A.Brohan,N.Brown,Y.Chebotar,O.Cortes,B.David,C.Finn,K.Gopalakrishnan,K.Hausman,
A.Herzog,etal. DoasIcan,notasIsay: Groundinglanguageinroboticaffordances. arXivpreprint
arXiv:2204.01691, 2022.
J.-B. Alayrac, J. Donahue, P. Luc, A. Miech, I. Barr, Y. Hasson, K. Lenc, A. Mensch, K. Millican,
M. Reynolds, et al. Flamingo: a visual language model for few-shot learning. arXiv preprint
arXiv:2204.14198, 2022.
R.Anil,A.M.Dai,O.Firat,M.Johnson,D.Lepikhin,A.Passos,S.Shakeri,E.Taropa,P.Bailey,Z.Chen,
et al. Palm 2 technical report. arXiv preprint arXiv:2305.10403, 2023.
A. Brohan, N. Brown, J. Carbajal, Y. Chebotar, J. Dabis, C. Finn, K. Gopalakrishnan, K. Hausman,
A. Herzog, J. Hsu, et al. Rt-1: Robotics transformer for real-world control at scale. arXiv preprint
arXiv:2212.06817, 2022.
T. Brown, B. Mann, N. Ryder, M. Subbiah, J. D. Kaplan, P. Dhariwal, A. Neelakantan, P. Shyam,
G. Sastry, A. Askell, et al. Language models are few-shot learners. Advances in neural information
processing systems, 33:1877–1901, 2020.
D.Cer,Y.Yang,S.Kong,N.Hua,N.Limtiaco,R.S.John,N.Constant,M.Guajardo-Cespedes,S.Yuan,
C. Tar, Y. Sung, B. Strope, and R. Kurzweil. Universal sentence encoder. CoRR, abs/1803.11175,
2018. URL http://arxiv.org/abs/1803.11175.
M. Chen, J. Tworek, H. Jun, Q. Yuan, H. P. d. O. Pinto, J. Kaplan, H. Edwards, Y. Burda,
N. Joseph, G. Brockman, et al. Evaluating large language models trained on code. arXiv preprint
arXiv:2107.03374, 2021.
X.Chen,J.Djolonga,P.Padlewski,B.Mustafa,S.Changpinyo,J.Wu,C.R.Ruiz,S.Goodman,X.Wang,
Y. Tay, S. Shakeri, M. Dehghani, D. Salz, M. Lucic, M. Tschannen, A. Nagrani, H. Hu, M. Joshi,
B. Pang, C. Montgomery, P. Pietrzyk, M. Ritter, A. Piergiovanni, M. Minderer, F. Pavetic, A. Waters,
G. Li, I. Alabdulmohsin, L. Beyer, J. Amelot, K. Lee, A. P. Steiner, Y. Li, D. Keysers, A. Arnab, Y. Xu,
K. Rong, A. Kolesnikov, M. Seyedhosseini, A. Angelova, X. Zhai, N. Houlsby, and R. Soricut. Pali-x:
On scaling up a multilingual vision and language model, 2023a.
X. Chen, X. Wang, S. Changpinyo, A. Piergiovanni, P. Padlewski, D. Salz, S. Goodman, A. Grycner,
B. Mustafa, L. Beyer, A. Kolesnikov, J. Puigcerver, N. Ding, K. Rong, H. Akbari, G. Mishra, L. Xue,
A. Thapliyal, J. Bradbury, W. Kuo, M. Seyedhosseini, C. Jia, B. K. Ayan, C. Riquelme, A. Steiner,
A.Angelova,X.Zhai,N.Houlsby,andR.Soricut. Pali: Ajointly-scaledmultilinguallanguage-image
model, 2023b.
K. Cobbe, V. Kosaraju, M. Bavarian, M. Chen, H. Jun, L. Kaiser, M. Plappert, J. Tworek, J. Hilton,
R. Nakano, et al. Training verifiers to solve math word problems. arXiv preprint arXiv:2110.14168,
2021.
Z.J.Cui,Y.Wang,N.Muhammad,L.Pinto,etal. Fromplaytopolicy: Conditionalbehaviorgeneration
from uncurated robot data. arXiv preprint arXiv:2210.10047, 2022.
S. Dasari and A. Gupta. Transformers for one-shot visual imitation. In Conference on Robot Learning,
pages 2071–2084. PMLR, 2021.
S. Dasari, F. Ebert, S. Tian, S. Nair, B. Bucher, K. Schmeckpeper, S. Singh, S. Levine, and C. Finn.
Robonet: Large-scale multi-robot learning. In Conference on Robot Learning, 2019.
13

--- Page 14 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
M.Dehghani,J.Djolonga,B.Mustafa,P.Padlewski,J.Heek,J.Gilmer,A.Steiner,M.Caron,R.Geirhos,
I.Alabdulmohsin,R.Jenatton,L.Beyer,M.Tschannen,A.Arnab,X.Wang,C.Riquelme,M.Minderer,
J. Puigcerver, U. Evci, M. Kumar, S. van Steenkiste, G. F. Elsayed, A. Mahendran, F. Yu, A. Oliver,
F. Huot, J. Bastings, M. P. Collier, A. Gritsenko, V. Birodkar, C. Vasconcelos, Y. Tay, T. Mensink,
A.Kolesnikov,F.Pavetić,D.Tran,T.Kipf,M.Lučić,X.Zhai,D.Keysers,J.Harmsen,andN.Houlsby.
Scaling vision transformers to 22 billion parameters, 2023.
D. Driess, F. Xia, M. S. Sajjadi, C. Lynch, A. Chowdhery, B. Ichter, A. Wahid, J. Tompson, Q. Vuong,
T. Yu, et al. Palm-e: An embodied multimodal language model. arXiv preprint arXiv:2303.03378,
2023.
M. Du, S. Nair, D. Sadigh, and C. Finn. Behavior retrieval: Few-shot imitation learning by querying
unlabeled datasets. arXiv preprint arXiv:2304.08742, 2023a.
Y.Du,K.Konyushkova,M.Denil,A.Raju,J.Landon,F.Hill,N.deFreitas,andS.Cabi. Vision-language
models as success detectors. arXiv preprint arXiv:2303.07280, 2023b.
C. Finn and S. Levine. Deep visual foresight for planning robot motion. In 2017 IEEE International
Conference on Robotics and Automation (ICRA), pages 2786–2793. IEEE, 2017.
C.Finn,T.Yu,T.Zhang,P.Abbeel,andS.Levine. One-shotvisualimitationlearningviameta-learning.
In Conference on robot learning, pages 357–368. PMLR, 2017.
R. A. Fisher. Design of experiments. British Medical Journal, 1(3923):554, 1936.
S. Y. Gadre, M. Wortsman, G. Ilharco, L. Schmidt, and S. Song. Clip on wheels: Zero-shot object
navigation as object localization and exploration. arXiv preprint arXiv:2203.10421, 2022.
Z.Gan,L.Li,C.Li,L.Wang,Z.Liu,J.Gao,etal. Vision-languagepre-training: Basics,recentadvances,
and future trends. Foundations and Trends® in Computer Graphics and Vision, 14(3–4):163–352,
2022.
G. Ghiasi, X. Gu, Y. Cui, and T.-Y. Lin. Open-vocabulary image segmentation. arXiv preprint
arXiv:2112.12143, 2021.
K. Grauman, A. Westbury, E. Byrne, Z. Chavis, A. Furnari, R. Girdhar, J. Hamburger, H. Jiang,
M. Liu, X. Liu, M. Martin, T. Nagarajan, I. Radosavovic, S. K. Ramakrishnan, F. Ryan, J. Sharma,
M. Wray, M. Xu, E. Z. Xu, C. Zhao, S. Bansal, D. Batra, V. Cartillier, S. Crane, T. Do, M. Doulaty,
A. Erapalli, C. Feichtenhofer, A. Fragomeni, Q. Fu, A. Gebreselasie, C. Gonzalez, J. Hillis, X. Huang,
Y. Huang, W. Jia, W. Khoo, J. Kolar, S. Kottur, A. Kumar, F. Landini, C. Li, Y. Li, Z. Li, K. Mangalam,
R. Modhugu, J. Munro, T. Murrell, T. Nishiyasu, W. Price, P. R. Puentes, M. Ramazanova, L. Sari,
K. Somasundaram, A. Southerland, Y. Sugano, R. Tao, M. Vo, Y. Wang, X. Wu, T. Yagi, Z. Zhao,
Y. Zhu, P. Arbelaez, D. Crandall, D. Damen, G. M. Farinella, C. Fuegen, B. Ghanem, V. K. Ithapu,
C.V.Jawahar,H.Joo,K.Kitani,H.Li,R.Newcombe,A.Oliva,H.S.Park,J.M.Rehg,Y.Sato,J.Shi,
M. Z. Shou, A. Torralba, L. Torresani, M. Yan, and J. Malik. Ego4d: Around the world in 3,000
hours of egocentric video, 2022.
X. Gu, T.-Y. Lin, W. Kuo, and Y. Cui. Open-vocabulary object detection via vision and language
knowledge distillation. arXiv preprint arXiv:2104.13921, 2021.
N. Hansen, R. Jangir, Y. Sun, G. Alenyà, P. Abbeel, A. A. Efros, L. Pinto, and X. Wang. Self-supervised
policy adaptation during deployment. arXiv preprint arXiv:2007.04309, 2020.
Y. Hao, H. Song, L. Dong, S. Huang, Z. Chi, W. Wang, S. Ma, and F. Wei. Language models are
general-purpose interfaces. arXiv preprint arXiv:2206.06336, 2022.
14

--- Page 15 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
F. Hill, S. Mokra, N. Wong, and T. Harley. Human instruction-following with deep reinforcement
learning via transfer-learning from text. arXiv preprint arXiv:2005.09382, 2020.
S. Huang, L. Dong, W. Wang, Y. Hao, S. Singhal, S. Ma, T. Lv, L. Cui, O. K. Mohammed, Q. Liu,
et al. Language is not all you need: Aligning perception with language models. arXiv preprint
arXiv:2302.14045, 2023.
W. Huang, P. Abbeel, D. Pathak, and I. Mordatch. Language models as zero-shot planners: Extracting
actionableknowledgeforembodiedagents. InInternationalConferenceonMachineLearning,pages
9118–9147. PMLR, 2022.
S. James, M. Bloesch, and A. J. Davison. Task-embedded control networks for few-shot imitation
learning. In Conference on robot learning, pages 783–795. PMLR, 2018.
E. Jang, A. Irpan, M. Khansari, D. Kappler, F. Ebert, C. Lynch, S. Levine, and C. Finn. Bc-z: Zero-
shot task generalization with robotic imitation learning. In Conference on Robot Learning, pages
991–1002. PMLR, 2021.
Y.Jiang,A.Gupta,Z.Zhang,G.Wang,Y.Dou,Y.Chen,L.Fei-Fei,A.Anandkumar,Y.Zhu,andL.Fan.
Vima: General robot manipulation with multimodal prompts. arXiv preprint arXiv:2210.03094,
2022.
L. P. Kaelbling. The foundation of efficient robot learning. Science, 369(6506):915–916, 2020.
S. Karamcheti, S. Nair, A. S. Chen, T. Kollar, C. Finn, D. Sadigh, and P. Liang. Language-driven
representation learning for robotics. arXiv preprint arXiv:2302.12766, 2023.
A. Kirillov, E. Mintun, N. Ravi, H. Mao, C. Rolland, L. Gustafson, T. Xiao, S. Whitehead, A. C. Berg,
W.-Y. Lo, et al. Segment anything. arXiv preprint arXiv:2304.02643, 2023.
I. Kostrikov, D. Yarats, and R. Fergus. Image augmentation is all you need: Regularizing deep
reinforcement learning from pixels. arXiv preprint arXiv:2004.13649, 2020.
M. Laskin, K. Lee, A. Stooke, L. Pinto, P. Abbeel, and A. Srinivas. Reinforcement learning with
augmented data. Advances in neural information processing systems, 33:19884–19895, 2020a.
M.Laskin,A.Srinivas,andP.Abbeel.Curl: Contrastiveunsupervisedrepresentationsforreinforcement
learning. In International Conference on Machine Learning, pages 5639–5650. PMLR, 2020b.
S.Levine,P.Pastor,A.Krizhevsky,J.Ibarz,andD.Quillen. Learninghand-eyecoordinationforrobotic
grasping with deep learning and large-scale data collection. The International journal of robotics
research, 37(4-5):421–436, 2018.
A. Lewkowycz, A. Andreassen, D. Dohan, E. Dyer, H. Michalewski, V. Ramasesh, A. Slone, C. Anil,
I. Schlag, T. Gutman-Solo, et al. Solving quantitative reasoning problems with language models.
arXiv preprint arXiv:2206.14858, 2022.
J. Li, D. Li, S. Savarese, and S. Hoi. Blip-2: Bootstrapping language-image pre-training with frozen
image encoders and large language models. arXiv preprint arXiv:2301.12597, 2023.
L.H.Li,M.Yatskar,D.Yin,C.-J.Hsieh,andK.-W.Chang. Visualbert: Asimpleandperformantbaseline
for vision and language. arXiv preprint arXiv:1908.03557, 2019.
H. Liu, L. Lee, K. Lee, and P. Abbeel. Instruction-following agents with jointly pre-trained vision-
language models. arXiv preprint arXiv:2210.13431, 2022.
15

--- Page 16 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
J. Lu, D. Batra, D. Parikh, and S. Lee. Vilbert: Pretraining task-agnostic visiolinguistic representations
for vision-and-language tasks. Advances in neural information processing systems, 32, 2019.
C. Lynch and P. Sermanet. Language conditioned imitation learning over unstructured data. arXiv
preprint arXiv:2005.07648, 2020.
C.Lynch,A.Wahid,J.Tompson,T.Ding,J.Betker,R.Baruch,T.Armstrong,andP.Florence.Interactive
language: Talking to robots in real time. arXiv preprint arXiv:2210.06407, 2022.
Y.J.Ma,S.Sodhani,D.Jayaraman,O.Bastani,V.Kumar,andA.Zhang. Vip: Towardsuniversalvisual
reward and representation via value-implicit pre-training. arXiv preprint arXiv:2210.00030, 2022.
Y. J. Ma, W. Liang, V. Som, V. Kumar, A. Zhang, O. Bastani, and D. Jayaraman. Liv: Language-image
representations and rewards for robotic control. arXiv preprint arXiv:2306.00958, 2023.
J. Mahler, J. Liang, S. Niyaz, M. Laskey, R. Doan, X. Liu, J. A. Ojea, and K. Goldberg. Dex-net 2.0:
Deep learning to plan robust grasps with synthetic point clouds and analytic grasp metrics. arXiv
preprint arXiv:1703.09312, 2017.
A.Majumdar,K.Yadav,S.Arnaud,Y.J.Ma,C.Chen,S.Silwal,A.Jain,V.-P.Berges,P.Abbeel,J.Malik,
et al. Where are we in the search for an artificial visual cortex for embodied intelligence? arXiv
preprint arXiv:2303.18240, 2023a.
A.Majumdar,K.Yadav,S.Arnaud,Y.J.Ma,C.Chen,S.Silwal,A.Jain,V.-P.Berges,P.Abbeel,J.Malik,
et al. Where are we in the search for an artificial visual cortex for embodied intelligence? arXiv
preprint arXiv:2303.18240, 2023b.
O. Mees, L. Hermann, and W. Burgard. What matters in language conditioned robotic imitation
learning over unstructured data. IEEE Robotics and Automation Letters, 7(4):11205–11212, 2022.
M. Minderer, A. Gritsenko, A. Stone, M. Neumann, D. Weissenborn, A. Dosovitskiy, A. Mahendran,
A. Arnab, M. Dehghani, Z. Shen, et al. Simple open-vocabulary object detection with vision
transformers. arXiv preprint arXiv:2205.06230, 2022.
Y.Mu,Q.Zhang,M.Hu,W.Wang,M.Ding,J.Jin,B.Wang,J.Dai,Y.Qiao,andP.Luo. Embodiedgpt:
Vision-language pre-training via embodied chain of thought. arXiv preprint arXiv:2305.15021,
2023.
S.Nair,E.Mitchell,K.Chen,S.Savarese,C.Finn,etal. Learninglanguage-conditionedrobotbehavior
fromofflinedataandcrowd-sourcedannotation. InConferenceonRobotLearning,pages1303–1315.
PMLR, 2022a.
S. Nair, A. Rajeswaran, V. Kumar, C. Finn, and A. Gupta. R3m: A universal visual representation for
robot manipulation. arXiv preprint arXiv:2203.12601, 2022b.
OpenAI. Gpt-4 technical report, 2023.
J.Pari,N.M.Shafiullah,S.P.Arunachalam,andL.Pinto. Thesurprisingeffectivenessofrepresentation
learning for visual imitation. arXiv preprint arXiv:2112.01511, 2021.
L. Pinto and A. Gupta. Supersizing self-supervision: Learning to grasp from 50k tries and 700 robot
hours. In 2016 IEEE international conference on robotics and automation (ICRA), pages 3406–3413.
IEEE, 2016.
S.Polu,J.M.Han,K.Zheng,M.Baksys,I.Babuschkin,andI.Sutskever. Formalmathematicsstatement
curriculum learning. arXiv preprint arXiv:2202.01344, 2022.
16

--- Page 17 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
V. H. Pong, M. Dalal, S. Lin, A. Nair, S. Bahl, and S. Levine. Skew-fit: State-covering self-supervised
reinforcement learning. arXiv preprint arXiv:1903.03698, 2019.
A. Radford, J. W. Kim, C. Hallacy, A. Ramesh, G. Goh, S. Agarwal, G. Sastry, A. Askell, P. Mishkin,
J. Clark, et al. Learning transferable visual models from natural language supervision. In Interna-
tional Conference on Machine Learning, pages 8748–8763. PMLR, 2021.
S.Reed,K.Zolna,E.Parisotto,S.G.Colmenarejo,A.Novikov,G.Barth-Maron,M.Gimenez,Y.Sulsky,
J. Kay, J. T. Springenberg, et al. A generalist agent. arXiv preprint arXiv:2205.06175, 2022.
M.Ryoo,A.Piergiovanni,A.Arnab,M.Dehghani,andA.Angelova. Tokenlearner: Adaptivespace-time
tokenizationforvideos. AdvancesinNeuralInformationProcessingSystems,34:12786–12797,2021.
D.Shah,B.Osiński,b.ichter,andS.Levine. Lm-nav: Roboticnavigationwithlargepre-trainedmodels
of language, vision, and action. In K. Liu, D. Kulic, and J. Ichnowski, editors, Proceedings of The 6th
Conference on Robot Learning, volume 205 of Proceedings of Machine Learning Research, pages 492–
504.PMLR,14–18Dec2023. URLhttps://proceedings.mlr.press/v205/shah23b.html.
R. Shah and V. Kumar. Rrl: Resnet as representation for reinforcement learning. arXiv preprint
arXiv:2107.03380, 2021.
M.Shridhar,L.Manuelli,andD.Fox. Cliport: Whatandwherepathwaysforroboticmanipulation. In
Proceedings of the 5th Conference on Robot Learning (CoRL), 2021.
M.Shridhar,L.Manuelli,andD.Fox. Cliport: Whatandwherepathwaysforroboticmanipulation. In
Conference on Robot Learning, pages 894–906. PMLR, 2022a.
M. Shridhar, L. Manuelli, and D. Fox. Perceiver-actor: A multi-task transformer for robotic manipula-
tion. arXiv preprint arXiv:2209.05451, 2022b.
I. Singh, V. Blukis, A. Mousavian, A. Goyal, D. Xu, J. Tremblay, D. Fox, J. Thomason, and A. Garg.
Progprompt: Generating situated robot task plans using large language models. In ICRA, 2023.
M. H. Smith and L. S. Coles. Design of a low cost, general purpose robot. In IJCAI, pages 324–336,
1973.
A. Stone, T. Xiao, Y. Lu, K. Gopalakrishnan, K.-H. Lee, Q. Vuong, P. Wohlhart, B. Zitkovich, F. Xia,
C. Finn, et al. Open-world object manipulation using pre-trained vision-language models. arXiv
preprint arXiv:2303.00905, 2023.
T. Sumers, K. Marino, A. Ahuja, R. Fergus, and I. Dasgupta. Distilling internet-scale vision-language
models into embodied agents. arXiv preprint arXiv:2301.12507, 2023.
Y. Tay, M. Dehghani, V. Q. Tran, X. Garcia, J. Wei, X. Wang, H. W. Chung, S. Shakeri, D. Bahri,
T. Schuster, H. S. Zheng, D. Zhou, N. Houlsby, and D. Metzler. Ul2: Unifying language learning
paradigms, 2023.
S. Vemprala, R. Bonatti, A. Bucker, and A. Kapoor. Chatgpt for robotics: Design principles and model
abilities. Microsoft Auton. Syst. Robot. Res, 2:20, 2023.
J.Wang,Z.Yang,X.Hu,L.Li,K.Lin,Z.Gan,Z.Liu,C.Liu,andL.Wang.Git: Agenerativeimage-to-text
transformer for vision and language. arXiv preprint arXiv:2205.14100, 2022.
J. Wei, X. Wang, D. Schuurmans, M. Bosma, E. Chi, Q. Le, and D. Zhou. Chain of thought prompting
elicits reasoning in large language models. arXiv preprint arXiv:2201.11903, 2022.
17

--- Page 18 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
J. Wei, L. Hou, A. Lampinen, X. Chen, D. Huang, Y. Tay, X. Chen, Y. Lu, D. Zhou, T. Ma, and Q. V. Le.
Symbol tuning improves in-context learning in language models, 2023.
J. Wu, R. Antonova, A. Kan, M. Lepert, A. Zeng, S. Song, J. Bohg, S. Rusinkiewicz, and T. Funkhouser.
Tidybot: Personalizedrobotassistancewithlargelanguagemodels.arXivpreprintarXiv:2305.05658,
2023.
T. Xiao, H. Chan, P. Sermanet, A. Wahid, A. Brohan, K. Hausman, S. Levine, and J. Tompson.
Robotic skill acquisition via instruction augmentation with vision-language models. arXiv preprint
arXiv:2211.11736, 2022a.
T. Xiao, I. Radosavovic, T. Darrell, and J. Malik. Masked visual pre-training for motor control. arXiv
preprint arXiv:2203.06173, 2022b.
S. Young, D. Gandhi, S. Tulsiani, A. Gupta, P. Abbeel, and L. Pinto. Visual imitation made easy. In
Conference on Robot Learning, pages 1992–2005. PMLR, 2021.
K.-T.Yu,M.Bauza,N.Fazeli,andA.Rodriguez. Morethanamillionwaystobepushed.ahigh-fidelity
experimental dataset of planar pushing. In 2016 IEEE/RSJ international conference on intelligent
robots and systems (IROS), pages 30–37. IEEE, 2016.
T.Yu,C.Finn,A.Xie,S.Dasari,T.Zhang,P.Abbeel,andS.Levine. One-shotimitationfromobserving
humans via domain-adaptive meta-learning. arXiv preprint arXiv:1802.01557, 2018.
X. Zhai, A. Kolesnikov, N. Houlsby, and L. Beyer. Scaling vision transformers. In Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 12104–12113, 2022.
X.Zhang,Y.Ding,S.Amiri,H.Yang,A.Kaminski,C.Esselink,andS.Zhang. Groundingclassicaltask
planners via vision-language models. arXiv preprint arXiv:2304.08587, 2023.
18

--- Page 19 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
A. Contributions
• Training and Evaluations (designing and executing procedures for training models, evalu-
ating models in simulation and the real world, running ablations for algorithm design
choices): Yevgen Chebotar, Krzysztof Choromanski, Tianli Ding, Danny Driess, Avinava Dubey,
Pete Florence, Chuyuan Fu, Montse Gonzalez Arenas, Keerthana Gopalakrishnan, Kehang Han,
Alexander Herzog, Brian Ichter, Alex Irpan, Isabel Leal, Lisa Lee, Yao Lu, Henryk Michalewski,
Igor Mordatch, Karl Pertsch, Michael Ryoo, Anikait Singh, Quan Vuong, Ayzaan Wahid, Paul
Wohlhart, Fei Xia, Ted Xiao, and Tianhe Yu.
• Network Architecture (designing and implementing model network modules, working on
tokenization of actions, enabling inference of the model networks during experiments):
Yevgen Chebotar, Xi Chen, Krzysztof Choromanski, Danny Driess, Pete Florence, Keerthana
Gopalakrishnan, Kehang Han, Karol Hausman, Brian Ichter, Alex Irpan, Isabel Leal, Lisa Lee,
Henryk Michalewski, Igor Mordatch, Kanishka Rao, Michael Ryoo, Anikait Singh, Quan Vuong,
Ayzaan Wahid, Jialin Wu, Fei Xia, Ted Xiao, and Tianhe Yu.
• Data Collection (collecting data on real robots, running real robot evaluations, executing
operations required for running real robots): Noah Brown, Justice Carbajal, Tianli Ding,
Krista Reymann, Grecia Salazar, Pierre Sermanet, Jaspiar Singh, Huong Tran, Stefan Welker,
and Sichun Xu.
• Leadership (leading the project efforts, managing the project staff, advising on project
directions): Yevgen Chebotar, Chelsea Finn, Karol Hausman, Brian Ichter, Sergey Levine, Yao
Lu, Igor Mordatch, Kanishka Rao, Pannag Sanketi, Radu Soricut, Vincent Vanhoucke, and
Tianhe Yu.
• Paper (working on the paper manuscript, designing paper visualizations and figures):
Yevgen Chebotar, Danny Driess, Chelsea Finn, Pete Florence, Karol Hausman, Brian Ichter, Lisa
Lee,SergeyLevine,IgorMordatch,KarlPertsch,QuanVuong,FeiXia,TedXiao,andTianheYu.
• Infrastructure (working on infrastructure and code base backbone needed for training
models, running experiments, storing and accessing data): AnthonyBrohan,YevgenChebo-
tar,DannyDriess,KehangHan,JasmineHsu,BrianIchter,AlexIrpan,NikhilJoshi,RyanJulian,
Dmitry Kalashnikov, Yuheng Kuang, Isabel Leal, Lisa Lee, Tsang-Wei Edward Lee, Yao Lu, Igor
Mordatch, Quan Vuong, Ayzaan Wahid, Fei Xia, Ted Xiao, Peng Xu, and Tianhe Yu.
B. Datasets
The vision-language datasets are based on the dataset mixtures from Chen et al. (2023b) and Driess
et al. (2023). The bulk of this data consists of the WebLI dataset, which is around 10B image-text
pairs across 109 languages, filtered to the top 10% scoring cross-modal similarity examples to give
1B training examples. Many other captioning and vision question answering datasets are included
as well, and more info on the dataset mixtures can be found in Chen et al. (2023b) for RT-2-PaLI-X,
andDriessetal.(2023)forRT-2-PaLM-E.Whenco-fine-tuningRT-2-PaLI-X,wedonotusetheEpisodic
WebLI dataset described by Chen et al. (2023a).
The robotics dataset is based on the dataset from Brohan et al. (2022). This consists of demon-
stration episodes collected with a mobile manipulation robot. Each demonstration is annotated with
anaturallanguageinstructionfromoneofsevenskills: "PickObject","MoveObjectNearObject",
"PlaceObjectUpright","KnockObjectOver","OpenDrawer","CloseDrawer","PlaceObjectinto
Receptacle", and "Pick Object from Receptacle and place on the counter". Further details can
be found in Brohan et al. (2022).
RT-2-PaLI-X weights the robotics dataset such that it makes up about 50% of the training mixture
19

--- Page 20 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
for co-fine-tuning. RT-2-PaLM-E weights the robotics dataset to be about 66% of the training mixture.
FortheresultsonLanguage-TableinTable1,ourmodelistrainedontheLanguage-Tabledatasets
from Lynch et al. (2022). Our model is co-fine-tuned on several prediction tasks: (1) predict the
action, given two consecutive image frames and a text instruction; (2) predict the instruction, given
image frames; (3) predict the robot arm position, given image frames; (4) predict the number of
timesteps between given image frames; and (5)predict whether the task wassuccessful, given image
frames and the instruction.
C. Baselines
We compare our method to multiple state-of-the-art baselines that challenge different aspects of our
method. All of the baselines use the exact same robotic data.
• RT-1: Robotics Transformer 1 Brohan et al. (2022) is a transformer-based model that achieved
state-of-the-art performance on a similar suite of tasks when it was published. The model does
not use VLM-based pre-training so it provides an important data point demonstrating whether
VLM-based pre-training matters.
• VC-1: VC-1 Majumdar et al. (2023a) is a visual foundation model that uses pre-trained visual
representations specifically designed for robotics tasks. We use pre-trained representations
from the VC-1 ViT-L model. Since VC-1 does not include language conditioning, we add this by
separatelyembeddingthelanguagecommandviaUniversalSentenceEncoderCeretal.(2018)
to enable comparison to our method. In particular, we concatenate the resulting language
embedding tokens to the image tokens produced by VC-1, and pass the concatenated token
sequences through token learner Ryoo et al. (2021). The token sequences produced by token
learner are then consumed by an RT-1 decoder-only transformer model to predict robot action
tokens. We train the VC-1 baseline end-to-end and unfreeze the VC-1 weights during training,
since this led to far better results than using frozen VC-1 weights.
• R3M: R3M Nair et al. (2022b) is a similar method to VC-1 in that R3M uses pre-trained
visual-language representations to improve policy training. In this case the authors use Ego4D
datasetGraumanetal.(2022)ofhumanactivitiestolearntherepresentationthatisusedbythe
policy. Both VC-1 and R3M test different state-of-the-art representation learning methods as an
alternative to using a VLM. To obtain a language-conditioned policy from the R3M pretrained
representation, we follow the same procedure as described above for VC-1, except we use the
R3M ResNet50 model to obtain the image tokens, and unfreeze it during training.
• MOO: MOO Stone et al. (2023) is an object-centric approach, where a VLM is first used to
specifytheobjectofinterestinaformofasingle,coloredpixelintheoriginalimage. Thispixel-
modified image is then trained with an end-to-end policy to accomplish a set of manipulation
tasks. This baseline corresponds to a situation where a VLM is used as a separate module that
enhances perception but its representations are not used for policy learning.
D. VLMs for RT-2
The PaLI-X model architecture consists of a ViT-22B Dehghani et al. (2023) to process images, which
canacceptsequencesof𝑛images,leadingto𝑛×𝑘tokensperimage,where𝑘isthenumberofpatches
perimage. Theimagetokenspassingoveraprojectionlayeristhenconsumedbyanencoder-decoder
backbone of 32B parameters and 50 layers, similar to UL2 Tay et al. (2023), which jointly processes
text and images as embeddings to generate output tokens in an auto-regressive manner. The text
20

--- Page 21 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
inputusuallyconsistsofthetypeoftaskandanyadditionalcontext(e.g.,"Generatecaptionin ⟨lang⟩"
for captioning tasks or "Answer in ⟨lang⟩: question" for VQA tasks).
The PaLI-3B model trained on Language-Table (Table 1) uses a smaller ViT-G/14 (Zhai et al.,
2022) (2B parameters) to process images, and UL2-3B (Tay et al., 2023) for the encoder-decoder
network.
The PaLM-E model is based on a decoder-only LLM that projects robot data such as images and
text into the language token space and outputs text such as high-level plans. In the case of the
used PaLM-E-12B, the visual model used to project images to the language embedding space is
a ViT-4B Chen et al. (2023b). The concatenation of continuous variables to textual input allows
PaLM-E to be fully multimodal, accepting a wide variety of inputs such as multiple sensor modalities,
object-centric representations, scene representations and object entity referrals.
E. Training Details
We perform co-fine-tuning on pre-trained models from the PaLI-X (Chen et al., 2023a) 5B & 55B
model, PaLI (Chen et al., 2023b) 3B model and the PaLM-E (Driess et al., 2023) 12B model. For
RT-2-PaLI-X-55B, we use learning rate 1e-3 and batch size 2048 and co-fine-tune the model for
80K gradient steps whereas for RT-2-PaLI-X-5B, we use the same learning rate and batch size and
co-fine-tune the model for 270K gradient steps. For RT-2-PaLM-E-12B, we use learning rate 4e-4 and
batch size 512 to co-fine-tune the model for 1M gradient steps. Both models are trained with the
next token prediction objective, which corresponds to the behavior cloning loss in robot learning. For
RT-2-PaLI-3B model used for Language-Table results in Table 1, we use learning rate 1e-3 and batch
size 128 to co-fine-tune the model for 300K gradient steps.
F. Evaluation Details
F.1. Evaluation Scenarios
ForstudyingtheemergentcapabilitiesofRT-2inaquantitativemanner, westudyvariouschallenging
semanticevaluationscenariosthataimtomeasurecapabilitiessuchasreasoning,symbolunderstand-
ing, and human recognition. A visual overview of a subset of these scenes is provided in Figure 8,
and the full list of instructions used for quantiative evalution is shown in Table 3.
F.2. Evaluation Instructions
Table2listsnaturallanguageinstructionsusedinmodelevaluationsforunseenobjects,backgrounds,
and environments. Each instruction was run between 1-5 times, depending on the number of total
instructions in that evaluation set. Table 3 lists natural language instructions used to evaluate
quantitative emergent evals. Each instruction was run 5 times.
21

--- Page 22 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
(a) Reasoning
“move coke can to
“move apple to cup with “move banna near the “déplacer les frites verts “pick a healthy drink” Taylor Swift”
same color” sum of two plus one” dans la tasse rouge”
“move coke can to
person with glasses”
“move coke can “put coke can close “move banana to “move apple to tree”
near Y” to dog” android” (c) Human
(b) Symbol Understanding Recognition
Figure8 | AnoverviewofsomeoftheevaluationscenariosusedtostudytheemergentcapabilitiesofRT-2.
They focus on three broad categories, which are (a) reasoning, (b) symbol understanding, and (c) human
recognition. Thevisualizedinstructionsareasubsetofthefullinstructions,whicharelistedinAppendixF.2.
TaskGroup Tasks
Symbol Understand- movecokecannearX,movecokecannear3,movecokecannearY
ing: Symbol1
Symbol Understand- moveappletotree,moveappletoduck,moveappletoapple,moveapple
ing: Symbol2 tomatchingcard
Symbol Understand- putcokecanclosetodog,pushcokecanontopofheart,placecokecan
ing: Symbol3 abovestar
Reasoning: Math move banana to 2, move banna near the sum of two plus one, move
banana near the answer of three times two, move banana near the
smallestnumber
Reasoning: Logos movecuptogoogle,movecuptoandroid,movecuptoyoutube,move
cuptoasearchengine,movecuptoaphone
Reasoning: Nutrition getmeahealthysnack,pickahealthydrink,pickupasweetdrink,move
thehealthysnacktothehealthydrink,pickupasaltysnack
Reasoning: Colorand move apple to cup with same color, move apple to cup with different
Multilingual color,movegreenchipstomatchingcolorcup,moveappletovasoverde,
BewegenSiedenApfelindieroteTasse,movegreenchipstovasorojo,
muevelamanzanaalvasoverde,déplacerlesfritesvertsdanslatasse
rouge
Person Recognition: movecokecantotaylorswift,movecokecantotomcruise,movecoke
Celebrities cantosnoopdog
Person Recognition: movecokecantopersonwithglasses,movecokecantothemanwith
CelebA whitehair,movecokecantothebrunettelady
Table3 | Naturallanguageinstructionsusedforquantitativeemergentevalutions.
22

--- Page 23 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
G. Example Failure Cases
InFig.9weprovideexamplesofanotabletypeoffailurecaseintheLanguageTablesetting,withthe
RT-2 model not generalizing to unseen object dynamics. In these cases, although the model is able
to correctly attend to the language instruction and move to the first correct object, it is not able to
control the challenging dynamics of these objects, which are significantly different than the small set
ofblockobjectsthathavebeenseeninthisenvironmentLynchetal.(2022). Thenpensimplyrollsoff
the table (Fig. 9, left), while the banana’s center-of-mass is far from where the robot makes contact
(Fig. 9, right). We note that pushing dynamics are notoriously difficult to predict and control Yu et al.
(2016). We hypothesize that greater generalization in robot-environment interaction dynamics may
be possible by further scaling the datasets across diverse environments and objects – for example, in
this case, datasets that include similar types of more diverse pushing dynamics Dasari et al. (2019).
In addition, despite RT-2’s promising performance on real world manipulation tasks in qualitative
and quantitative emergent evaluations, we still find numerous notable failure cases. For example,
with the current training dataset composition and training method, RT-2 seemed to perform poorly
at:
• Grasping objects by specific parts, such as the handle
• Novel motions beyond what was seen in the robot data, such as wiping with a towel or tool use
• Dexterous or precise motions, such as folding a towel
• Extended reasoning requiring multiple layers of indirection
Push the red marker to the video game controller Push the banana to the apple
Figure9 | Qualitativeexamplefailurecasesinthereal-worldfailingtogeneralizetounseenobjectdynamics.
H. Quantitative Experimental Results
H.1. Overall Performance, for Section 4.1
Table 4 lists our quantitative overall evaluation results. We find that RT-2 performs as well or better
than baselines on seen tasks and significantly outperforms baselines on generalization to unseen
objects, backgrounds, and environments.
Model SeenTasks UnseenObjects UnseenBackgrounds UnseenEnvironments UnseenAverage
Easy Hard Easy Hard Easy Hard
R3M(Nairetal.,2022b) 45 32 14 13 9 0 2 12
VC-1(Majumdaretal.,2023a) 63 34 10 13 3 0 0 10
RT-1(Brohanetal.,2022) 92 31 43 71 9 26 14 32
MOO(Stoneetal.,2023) 75 58 48 38 41 19 3 35
RT-2-PaLI-X-55B(ours) 91 70 62 96 48 63 35 62
RT-2-PaLM-E-12B1(ours) 93 84 76 75 71 36 33 62
Table4 | OverallperformanceoftwoinstantiationsofRT-2andbaselinesacrossseentrainingtasksaswellas
unseenevaluationsmeasuringgeneralizationtonovelobjects,novelbackgrounds,andnovelenvironments.
23

--- Page 24 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
H.2. Emergent Evaluation, for Section 4.2
Table 5 lists all of our quantitative emergent evaluation results. We find that RT-2 performs 2x
to 3x better than RT-1 on these new instructions, without any additional robotic demonstrations.
This showcases how our method allows us to leverage capabilities from pretraining on web-scale
vision-language datasets.
Model SymbolUnderstanding Reasoning PersonRecognition Average
Symbol1 Symbol2 Symbol3 Average Math Logos Nutrition Color/Multilingual Average Celebrities CelebA Average
VC-1(Majumdaretal.,2023a) 7 25 0 11 0 8 20 13 10 20 7 13 11
RT-1(Brohanetal.,2022) 27 20 0 16 5 0 32 28 16 20 20 20 17
RT-2-PaLI-X-55B(ours) 93 60 93 82 25 52 48 58 46 53 53 53 60
RT-2-PaLM-E-12B(ours) 67 20 20 36 35 56 44 35 43 33 53 43 40
Table5 | PerformanceofRT-2andbaselinesonquantitativeemergentevaluations.
H.3. Size and Training Ablations, for Section 4.3
Table6detailsquantitativeresultsforablationsacrossmodelsizeandtrainingapproach. Acrosseach,
we see that model size plays an important role in performance and that co-fine-tuning outperforms
fine-tuning, which outperforms training from scratch.
Model Size Training UnseenObjects UnseenBackgrounds UnseenEnvironments Average
Easy Hard Easy Hard Easy Hard
RT-2-PaLI-X 5B fromscratch 0 10 46 0 0 0 9
RT-2-PaLI-X 5B fine-tuning 24 38 79 50 36 23 42
RT-2-PaLI-X 5B co-fine-tuning 60 38 67 29 44 24 44
RT-2-PaLI-X 55B fine-tuning 60 62 75 38 57 19 52
RT-2-PaLI-X 55B co-fine-tuning 70 62 96 48 63 35 63
Table6 | AblationsofRT-2showcasingtheimpactofparametercountandtrainingstrategyongeneralization.
I. Additional Chain-Of-Thought Reasoning Results
Wepresentadditionalexamplesofchain-of-thoughtreasoningrolloutsaccomplishedwithRT-2-PaLM-
E, as described in Sec. 4.4, in Figure 10.
1Theoriginalpre-trainingdatamixtureusedinPaLM-E-12B(asdescribedinDriessetal.(2023))includesrobotimages
forhigh-levelVQAplanningtasksthatcanbesimilartoimagesencounteredingeneralizationscenarios.However,noneof
thosetrainingexamplesincludelow-levelactionsthatareevaluatedinthisexperiment.
24

--- Page 25 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
User
Pick up the
object that is
different from all
other objects
Plan: Pick rxbar
chocolate
User
Move the green
objects together
Plan: Move green
can near green
rice chip bag
User
Move the blue
objects together
Plan: Move blue
chip bag near
pepsi
User
I am sleepy, bring
me a drink to
help.
Plan: Pick redbull
can
Figure10 | AdditionalexamplesofRT-2withchain-of-thoughtreasoning
25

--- Page 26 ---
RT-2:Vision-Language-ActionModelsTransferWebKnowledgetoRoboticControl
TaskGroup Tasks
Unseen Objects pickbanana,movebanananearcokecan,moveorangecannearbanana,
(Easy) pickoreo,moveoreonearapple,moveredbullcannearoreo,pickpear,
pickcoconutwater,movepearnearcoconutwater,movepepsicannear
pear
Unseen Objects pickcoldbrewcan,picklargeorangeplate,pickchewtoy,picklargeten-
(Hard) nisball,pickbirdornament,pickfishtoy,pickgingerlemonkombucha,
pick egg separator, pick wrist watch, pick green sprite can, pick blue
microfibercloth,pickyellowpear,pickpretzelchipbag,pickdisinfectant
wipes,pickpineapplehintwater,pickgreencup,pickpicklesnack,pick
small blue plate, pick small orange rolling pin, pick octopus toy, pick
catniptoy
Unseen Back- pickgreenjalapenochipbag,pickorangecan,pickpepsican,pick7up
grounds(Easy) can, pick apple, pick blue chip bag, pick orange, pick 7up can, move
orangenearsink,pickcokecan,picksponge,pickrxbarblueberry
Unseen Back- pick wrist watch, pick egg separator, pick green sprite can, pick blue
grounds(Hard) microfibercloth,pickyellowpear,pickpretzelchipbag,pickdisinfectant
wipes,pickpineapplehintwater,pickgreencup,pickpicklesnack,pick
small blue plate, pick small orange rolling pin, pick octopus toy, pick
catniptoy,pickswedishfishbag,picklargegreenrollingpin,pickblack
sunglasses
UnseenEnviron- pickcokecan,pickapple,pickrxbarblueberry,moveapplenearcokecan,
ments(Easy) moverxbarblueberrynearapple,movecokecannearrxbarblueberry,
pickblueplasticbottle,picksponge,pickbluechipbag,movesponge
near blue plastic bottle, move blue chip bag near sponge, move blue
plasticbottlenearbluechipbag,movecokecannearwhitemug,move
spongenearwhitemug,movecokecannearyellowbowl,movesponge
nearyellowbowl,movecokecanneargreencloth,movespongenear
greencloth,movecokecannearplate,movespongenearplate,move
coke can near spoon, move sponge near spoon, move coke can near
orangecup,movespongenearorangecup,pickwhitemug,pickyellow
bowl,pickgreencloth,movewhitemugnearsponge,moveyellowbowl
nearsponge,movegreenclothnearsponge,pickplate,pickspoon,pick
orange cup, move plate near sponge, move spoon near sponge, move
orangecupnearsponge,putcokecanintosink,dropcokecanintosink,
push coke can into sink, put sponge into sink, drop sponge into sink,
pushspongeintosink,putgreenclothintosink,dropgreenclothinto
sink,pushgreenclothintosink
UnseenEnviron- pickcokecan,pickapple,pickrxbarblueberry,moveapplenearcokecan,
ments(Hard) moverxbarblueberrynearapple,movecokecannearrxbarblueberry,
movecokecannearstapler,moveapplenearstapler,movecokecannear
keyboard, move apple near keyboard, move coke can near tissue box,
moveappleneartissuebox,movecokecannearpapers,moveapplenear
papers,movecokecannearmouse,moveapplenearmouse,movecoke
can near book, move apple near book, pick marker, pick stapler, pick
mouse,movemarkernearapple,movestaplernearapple,movemouse
nearapple,pushcokecantotheleft,pushcokecantotheright,push
spongetotheleft,pushspongetotheright,pushtissueboxtotheleft,
pushtissueboxtotheright,pointatcokecan,pointatsponge,pointat
tissuebox
Table 2 | Natural language instructions used for evaluations testing controlled distribution shifts along the
dimension of novel objects, novel environments, and novel backgrounds. For each category, we introduce
evaluationsettingswithsmallerdistributionshiftsaswellaslargerdistributionshifts. Avisualizationofthese
scenariosifshowninFigure3.
26