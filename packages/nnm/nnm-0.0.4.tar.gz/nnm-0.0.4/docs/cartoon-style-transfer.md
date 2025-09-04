### 2023
- StyO: Stylize Your Face in Only One-Shot \[[论文解读](https://mp.weixin.qq.com/s/jgwUtHkuqeAvtUXmsHjRUw)\] \[[PDF](https://arxiv.org/pdf/2303.03231.pdf)\]  
使用200张左右的真人图+1张风格图+文本提示模板微调stable diffusion实现图像重建，此时模型就可以根据不同的文本模板配置输出与目标风格相关的图像了，增加真实人脸对应的文本模板的content attention map交换操作之后可以显著改善生成的风格图与输入图的相关性。

### 2022
- VToonify: Controllable High-Resolution Portrait Video Style Transfer
\[[Code](https://github.com/williamyang1991/VToonify)\]
- Pastiche Master: Exemplar-Based High-Resolution Portrait Style Transfer
\[[Code](https://github.com/williamyang1991/DualStyleGAN)\]
- DCT-Net: Domain-Calibrated Translation for Portrait Stylization
\[[Code](https://github.com/menyifang/DCT-Net)\]
- WebtoonMe: A Data-Centric Approach for Full-Body Portrait Stylization
\[[Code](https://github.com/webtoon/WebtoonMe)\]
- Cross-Domain Style Mixing for Face Cartoonization
\[[Unofficial Code](https://github.com/hyoseok1223/CDSM)\]
- Interactive Cartoonization with Controllable Perceptual Factors
- Feature Statistics Mixing Regularization for Generative Adversarial Networks
\[[Code](https://github.com/naver-ai/FSMR)\]
- Learning to Generate Line Drawings that Convey Geometry and Semantics
\[[Code](https://github.com/carolineec/informative-drawings)\]
- JoJoGAN: One Shot Face Stylization
\[[Code](https://github.com/mchong6/JoJoGAN)\]  
首先使用e4e获取风格图对应的latent code，因为e4e是用真人训练的，所以得到的latent code生成的就是真人图，然后对分辨率较高的层的latent code进行随机的style mixing产生更多对应的真实人脸数据；此时就有了成对的数据：1张风格图-多张真实图，这也就是论文标题说的One Shot的意思，经过微调预训练模型后即可实现端到端的风格变换模型。

### 2021
- BlendGAN：Implicitly GAN Blending for Arbitrary Stylized Face Generation
\[[Code](https://github.com/onion-liu/BlendGAN)\]
- AniGAN: Style-Guided Generative Adversarial Networks for Unsupervised Anime Face Generation
\[[Code](https://github.com/bing-li-ai/AniGAN)\]
- Stylealign: Analysis and Applications of Aligned Stylegan Models
\[[Code](https://github.com/betterze/StyleAlign)\]
- StyleGAN of All Trades: Image Manipulation with Only Pretrained StyleGAN
\[[Code](https://github.com/mchong6/SOAT)\]
- CIPS-3D: A 3D-Aware Generator of GANs Based on Conditionally-Independent Pixel Synthesis
\[[Code](https://github.com/PeterouZh/CIPS-3D)\]
- Fine-Tuning StyleGAN2 For Cartoon Face Generation
\[[Code](https://github.com/happy-jihye/Cartoon-StyleGAN)\]
- AgileGAN: Stylizing Portraits by Inversion-Consistent Transfer Learning
\[[Unofficial Code](https://github.com/open-mmlab/MMGEN-FaceStylor)\]
- Unsupervised Image-to-Image Translation via Pre-trained StyleGAN2 Network
\[[Code](https://github.com/HideUnderBush/UI2I_via_StyleGAN2)\]

### 2020
- AutoToon: Automatic Geometric Warping for Face Cartoon Generation
\[[Code](https://github.com/adobe-research/AutoToon)\]
- Resolution Dependent GAN Interpolation for Controllable Image Synthesis Between Domains
\[[Code](https://github.com/justinpinkney/toonify)\]
- AnimeGAN: A Novel Lightweight GAN for Photo Animation
\[[Code](https://github.com/TachibanaYoshino/AnimeGAN)\]
- Few-shot Knowledge Transfer for Fine-grained Cartoon Face Generation
- U-GAT-IT: Unsupervised Generative Attentional Networks with Adaptive Layer-Instance Normalization for Image-to-Image Translation
\[[Tensorflow Code](https://github.com/taki0112/UGATIT)\] \[[PyTorch Code](https://github.com/znxlwm/UGATIT-pytorch)\]

### 2019
- Landmark Assisted CycleGAN for Cartoon Face Generation

### 2018
- CartoonGAN: Generative Adversarial Networks for Photo Cartoonization
\[[Code](https://github.com/FlyingGoblin/CartoonGAN)\]

### 2017
- Diversified Texture Synthesis with Feed-forward
\[[Code](https://github.com/Yijunmaverick/MultiTextureSynthesis)\]
