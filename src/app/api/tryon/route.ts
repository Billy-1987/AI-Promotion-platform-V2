import { NextRequest, NextResponse } from 'next/server'
import OpenAI from 'openai'

export const maxDuration = 120 // seconds

const client = new OpenAI({
  baseURL: 'https://openrouter.ai/api/v1',
  apiKey: process.env.OPENROUTER_API_KEY,
})

const STYLE_LABELS: Record<string, string> = {
  sport: 'sportswear', outdoor: 'outdoor', menswear: "men's fashion",
  womenswear: "women's fashion", kids: "children's fashion",
  trendy: 'streetwear trendy', vintage: 'vintage retro', workwear: 'business workwear',
}

const STYLE_ZH: Record<string, string> = {
  sport: '运动', outdoor: '户外', menswear: '男装', womenswear: '女装',
  kids: '儿童', trendy: '潮流', vintage: '复古', workwear: '上班通勤',
}

// Detailed background scene descriptions that will be injected into the image prompt
const BG_SCENES: Record<string, string> = {
  bg_sport1:  'a modern indoor sports gym with equipment, bright overhead lighting, polished floors',
  bg_sport2:  'an outdoor athletics running track with stadium stands, blue sky, natural sunlight',
  bg_outdoor1:'a lush mountain forest trail with dappled sunlight through tall trees, dense green foliage, mossy ground',
  bg_outdoor2:'a scenic rocky stream in nature with mossy boulders, crystal clear water, soft natural light',
  bg_men1:    'a sleek modern corporate lobby with marble floors, glass walls, and warm accent lighting',
  bg_men2:    'a vibrant urban city street with buildings, bokeh city lights, golden hour sunlight',
  bg_women1:  'a beautiful blooming garden courtyard with colorful flowers, soft natural light, warm tones',
  bg_women2:  'an upscale fashion boutique interior with elegant displays, warm spotlights, luxury feel',
  bg_kids1:   'a colorful amusement park with rides and balloons, bright cheerful atmosphere',
  bg_kids2:   'a bright modern classroom with colorful decorations, warm natural window light',
  bg_trendy1: 'a graffiti-covered street art district with bold murals, urban gritty atmosphere',
  bg_trendy2: 'a neon-lit night market with glowing signs, vibrant colors, atmospheric night scene',
  bg_vintage1:'a cozy vintage retro cafe with warm Edison bulbs, wooden furniture, nostalgic atmosphere',
  bg_vintage2:'a charming old town alley with brick walls, cobblestone street, warm afternoon light',
  bg_work1:   'a modern open-plan office with large windows, city view, clean minimalist design',
  bg_work2:   'a professional conference room with a long table, city skyline view, polished corporate feel',
  // 鞋子专属背景
  bg_shoe1:   'a warm natural wooden floor surface, soft side lighting, clean minimal studio feel',
  bg_shoe2:   'lush green outdoor grass lawn, natural daylight, fresh outdoor atmosphere',
  bg_shoe3:   'a busy urban city sidewalk with concrete pavement, street life in background, golden hour light',
  bg_shoe4:   'a clean white minimalist studio surface, soft diffused lighting, pure product photography setup',
  bg_shoe5:   'a rustic cobblestone stone pavement path, warm afternoon sunlight, vintage outdoor atmosphere',
  bg_shoe6:   'an outdoor sports court with court markings, bright natural sunlight, athletic environment',
}

// Model descriptions — explicitly Western/European appearance, young 25-30
const MODEL_BY_STYLE: Record<string, string> = {
  sport:     'a fit athletic Western European model (age 25-30), energetic sporty pose',
  outdoor:   'a handsome young Caucasian male model (age 25-30), adventurous outdoor look',
  menswear:  'a handsome young Caucasian male model (age 25-30), sharp jawline, confident sunny smile, athletic build',
  womenswear:'a beautiful young European female model (age 25-30), slender figure, sweet charming smile, radiant skin',
  kids:      'a cute Western child model matching the clothing age',
  trendy:    'a cool young Caucasian streetwear model (age 25-30), urban attitude, stylish look',
  vintage:   'a stylish young European model (age 25-30), vintage charm, warm smile',
  workwear:  'a polished young Caucasian professional model (age 25-30), confident business look',
}

type ImagePart = { type: 'image_url'; image_url: { url: string } }
type TextPart = { type: 'text'; text: string }
type ContentPart = ImagePart | TextPart

async function generateImage(parts: ContentPart[], model: string): Promise<string | null> {
  const response = await client.chat.completions.create({
    model,
    messages: [{ role: 'user', content: parts as OpenAI.Chat.ChatCompletionContentPart[] }],
  })
  const msg = response.choices[0]?.message as unknown as Record<string, unknown>
  const images = msg?.images as Array<{ image_url: { url: string } }> | undefined
  return images?.[0]?.image_url?.url ?? null
}

const ANALYZE_PROMPT = `Analyze this product image. Return pure JSON only (no markdown):
{"style":"sport|outdoor|menswear|womenswear|kids|trendy|vintage|workwear","productCategory":"shoes|clothing","colors":["color1"],"keywords":["kw1","kw2"]}`

export async function POST(req: NextRequest) {
  const { clothingBase64, clothingMime, style: inputStyle, backgroundId, productCategory: inputCategory, skipAnalyze } = await req.json()

  if (!clothingBase64) {
    return NextResponse.json({ error: 'No clothing image provided' }, { status: 400 })
  }

  const clothingPart: ContentPart = {
    type: 'image_url',
    image_url: { url: `data:${clothingMime ?? 'image/jpeg'};base64,${clothingBase64}` },
  }

  // If style/category already known (re-generate flow), skip analyze
  let resolvedStyle = inputStyle ?? 'womenswear'
  let resolvedCategory = inputCategory ?? 'clothing'
  let analyzeData: Record<string, unknown> | null = null

  const analyzePromise = skipAnalyze
    ? Promise.resolve(null)
    : client.chat.completions.create({
        model: 'google/gemini-2.5-flash',
        messages: [{ role: 'user', content: [clothingPart, { type: 'text', text: ANALYZE_PROMPT }] as OpenAI.Chat.ChatCompletionContentPart[] }],
      }).then(res => {
        const text = res.choices[0]?.message?.content ?? ''
        try {
          const json = JSON.parse(text.trim())
          resolvedStyle = json.style ?? resolvedStyle
          resolvedCategory = json.productCategory ?? resolvedCategory
          analyzeData = json
        } catch {
          const m = text.match(/\{[\s\S]*?\}/)
          if (m) {
            try {
              const json = JSON.parse(m[0])
              resolvedStyle = json.style ?? resolvedStyle
              resolvedCategory = json.productCategory ?? resolvedCategory
              analyzeData = json
            } catch { /* keep defaults */ }
          }
        }
        return analyzeData
      }).catch(() => null)

  // Use inputCategory if known (re-generate), otherwise default to clothing for prompt
  // The image model will identify the product type itself from the image
  const isShoes = inputCategory === 'shoes'
  const styleLabel = STYLE_LABELS[inputStyle ?? 'womenswear'] ?? 'fashion'
  const styleZhLabel = STYLE_ZH[inputStyle ?? 'womenswear'] ?? '时尚'
  const bgScene = BG_SCENES[backgroundId] ?? 'a clean studio with soft white lighting'
  const modelDesc = MODEL_BY_STYLE[inputStyle ?? 'womenswear'] ?? 'a handsome young Caucasian model (age 25-30)'

  const imagePrompt = isShoes
    ? `Professional shoe product photo. Extract exact shoe design/colors/materials from input. NO person or body parts. Place shoes on: ${bgScene}. Arrange naturally, slightly angled. Professional lighting, soft shadows. High-quality commercial product photo.`
    : `Professional ${styleLabel} fashion photo. IGNORE any person in input image — extract clothing design/colors/patterns/cut only. New virtual model: ${modelDesc}, Western/European, age 25-30, NOT Asian. Model wears EXACTLY the extracted clothing. Background: ${bgScene}. Photorealistic full-body or 3/4 shot, fashion editorial quality.`

  const textPrompt = isShoes
    ? `分析这双鞋的设计特点、材质工艺和适合场景。返回纯JSON（无markdown代码块）：{"description":"100字内专业鞋款描述，突出设计亮点和穿着场景","fitScore":85,"styleMatch":"风格特点","occasion":"适合场合"}`
    : `分析这件${styleZhLabel}服装的上身效果、版型特点和适合人群。返回纯JSON（无markdown代码块）：{"description":"100字内专业上身效果描述","fitScore":85,"styleMatch":"风格特点","occasion":"适合场合"}`

  const [imageRes, textRes] = await Promise.allSettled([
    Promise.race([
      generateImage(
        [clothingPart, { type: 'text', text: imagePrompt }],
        'google/gemini-2.5-flash-image',
      ),
      generateImage(
        [clothingPart, { type: 'text', text: imagePrompt }],
        'google/gemini-3.1-flash-image-preview',
      ),
    ]),
    client.chat.completions.create({
      model: 'google/gemini-2.5-flash',
      messages: [{ role: 'user', content: [clothingPart, { type: 'text', text: textPrompt }] as OpenAI.Chat.ChatCompletionContentPart[] }],
    }),
  ])

  // Wait for analyze to finish (it was running in parallel)
  await analyzePromise

  const generatedImageUrl = imageRes.status === 'fulfilled' ? imageRes.value : null

  let analysis = { description: '', fitScore: 80, styleMatch: '', occasion: '' }
  if (textRes.status === 'fulfilled') {
    const text = textRes.value.choices[0]?.message?.content ?? ''
    try {
      analysis = JSON.parse(text.trim())
    } catch {
      const match = text.match(/\{[\s\S]*?\}/)
      if (match) {
        try { analysis = JSON.parse(match[0]) } catch { analysis.description = text.slice(0, 200) }
      } else {
        analysis.description = text.slice(0, 200)
      }
    }
  }

  return NextResponse.json({ ...analysis, generatedImageUrl, analyzeData })
}
