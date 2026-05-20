# 提示词指南

## 白瓷肌写实工作流

### 正向提示词
```
RAW photo, realistic photo, a beautiful young Chinese woman, pale porcelain white skin, fair complexion, rosy undertone, natural skin texture, slight pores visible, natural lip color, soft natural lighting, 85mm portrait lens, shallow depth of field, canon eos r5, photorealistic, 8k uhd, dslr, high quality, film grain
```

### 反向提示词
```
ng_deepnegative_v1_75t,(badhandv4:1.2),EasyNegative,(worst quality:2),illustration,anime,painting,drawing,art,sketch,3d render,plastic skin,airbrushed,oversmoothed,caricature,cartoon,tanned skin,dark skin,(hands:1.4),(exposed hands:1.3),(fingers:1.2),(holding:1.1),hand visible
```

## 写实超白皙版

### 正面提示词
```
best quality, masterpiece, ultra-detailed, RAW photo, realistic photo, photograph, a beautiful young Chinese woman, (very pale porcelain white skin:1.3), (fair snow white body:1.2), rosy undertone, natural skin texture with slight pores visible, fine skin details, natural lip color, flawless face, perfect skin, soft warm indoor lighting, 85mm portrait lens, shallow depth of field, canon eos r5, photorealistic, 8k uhd, dslr, high quality, film grain
```

### 负面提示词
```
ng_deepnegative_v1_75t,(badhandv4:1.2),EasyNegative,(worst quality:2),(low quality:2),lowres,normal quality,illustration,anime,painting,drawing,art,sketch,3d render,plastic skin,airbrushed,oversmoothed,caricature,cartoon,((monochrome)),((grayscale)),tanned skin,dark skin,yellow skin,freckles,moles,spots,blemishes,skin imperfection,acne,scars,skin spots,(bad anatomy:1.21),(bad proportions:1.331),(disfigured:1.331),extra limbs,(missing arms:1.331),(extra legs:1.331),(fused fingers:1.61051),(too many fingers:1.61051),(unclear eyes:1.331),(hands:1.4),(exposed hands:1.3),(fingers:1.2),(holding:1.1),hand visible
```

## 提示词模板

```
RAW photo, realistic photo, a beautiful young Chinese woman, {穿搭描述}, (very pale porcelain white skin:1.3), (fair snow white body:1.2), rosy undertone, natural skin texture, slight pores visible, natural lip color, {光线描述}, 85mm portrait lens, shallow depth of field, canon eos r5, photorealistic, 8k uhd, dslr, high quality, film grain, {构图描述}
```

## 穿搭参考

| 风格 | 提示词 |
|------|--------|
| 日常 | `wearing a white T-shirt` |
| 清凉 | `wearing a white sleeveless top` |
| 花园 | `wearing a white summer dress, straw hat` |
| 夜巷 | `wearing a black leather jacket` |
| 咖啡馆 | `wearing a beige knit sweater, holding a coffee cup` |
| 图书馆 | `wearing a plaid shirt, glasses` |
| 雨中 | `wearing a trench coat, holding a transparent umbrella` |
| 居家 | `wearing a comfortable cotton nightgown` |

## 光线描述

| 场景 | 提示词 |
|------|--------|
| 室内默认 | `soft warm indoor lighting` |
| 自然光 | `soft natural lighting` |
| 窗边 | `window light, soft diffused lighting` |
| 夜景 | `neon lights, cyberpunk lighting` |
| 暖光 | `warm golden hour lighting` |

## 构图描述

| 构图 | 提示词 |
|------|--------|
| 人像特写 | `close-up portrait` |
| 半身照 | `waist up portrait` |
| 大半身 | `mid-thigh up` |
| 全身站姿 | `full body` |

## 服装控制技巧

### 紧身T恤
正面：`(wearing a tight form-fitting [color] short-sleeve [neckline] cotton t-shirt:1.4), (snug bodycon fit:1.2), (tight stretchy fabric hugging her slim waist:1.1)`

负面：`(camisole:1.3),(tank top:1.3),(sleeveless:1.3),(crop top:1.2),(sports bra:1.2),(nude:1.5),(topless:1.5),(naked:1.5),(no shirt:1.3)`

## 闭眼控制技巧

正面：`(eyes gently closed:1.5),(softly closed eyelids:1.3)`

负面：`(open eyes:1.5)`