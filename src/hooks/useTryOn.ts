'use client'

import { useState, useCallback } from 'react'
import { TryOnState, TryOnResult, StyleTag } from '@/types'
import { suggestBackgrounds, generateTryOn } from '@/lib/mockAI'

export function useTryOn() {
  const [state, setState] = useState<TryOnState>({
    status: 'idle',
    modelPhotoFile: null,
    modelPhotoPreviewUrl: null,
    clothingFile: null,
    clothingPreviewUrl: null,
    detectedStyle: null,
    selectedBackground: null,
    resultUrl: null,
    tryOnResult: null,
    analysis: null,
  })

  const [suggestedBackgrounds, setSuggestedBackgrounds] = useState<string[]>([])

  const uploadClothing = useCallback(async (file: File) => {
    const previewUrl = URL.createObjectURL(file)
    setState(prev => ({
      ...prev,
      status: 'processing',
      clothingFile: file,
      clothingPreviewUrl: previewUrl,
      analysis: null,
      resultUrl: null,
      tryOnResult: null,
    }))

    // Generate immediately with default style, API will analyze in parallel
    const defaultStyle: StyleTag = 'womenswear'
    const defaultCategory: 'clothing' | 'shoes' = 'clothing'
    const backgrounds = suggestBackgrounds(defaultStyle, defaultCategory)
    setSuggestedBackgrounds(backgrounds)

    setState(prev => ({
      ...prev,
      detectedStyle: defaultStyle,
      selectedBackground: backgrounds[0],
    }))

    try {
      const result: TryOnResult = await generateTryOn(file, backgrounds[0], null, null, undefined)

      // Extract analyzed style/category from result
      const analyzedStyle = (result as any).analyzeData?.style ?? defaultStyle
      const analyzedCategory = (result as any).analyzeData?.productCategory ?? defaultCategory

      // Update backgrounds if style changed
      if (analyzedStyle !== defaultStyle || analyzedCategory !== defaultCategory) {
        const newBackgrounds = suggestBackgrounds(analyzedStyle, analyzedCategory)
        setSuggestedBackgrounds(newBackgrounds)
      }

      setState(prev => ({
        ...prev,
        status: 'result',
        resultUrl: result.previewUrl,
        tryOnResult: result,
        detectedStyle: analyzedStyle,
        analysis: (result as any).analyzeData ? {
          style: analyzedStyle,
          productCategory: analyzedCategory,
          colors: (result as any).analyzeData.colors ?? [],
          category: '',
          keywords: (result as any).analyzeData.keywords ?? [],
          backgroundSuggestion: '',
          productDescription: result.description ?? '',
        } : null,
      }))
    } catch {
      setState(prev => ({ ...prev, status: 'ready' }))
    }
  }, [])

  const selectBackground = useCallback((backgroundId: string) => {
    setState(prev => ({ ...prev, selectedBackground: backgroundId }))
  }, [])

  const selectStyle = useCallback((style: StyleTag) => {
    const productCategory = state.analysis?.productCategory ?? 'clothing'
    const backgrounds = suggestBackgrounds(style, productCategory)
    setSuggestedBackgrounds(backgrounds)
    setState(prev => ({ ...prev, detectedStyle: style, selectedBackground: backgrounds[0] }))
  }, [state.analysis])

  const generate = useCallback(async () => {
    if (!state.clothingFile || !state.selectedBackground) return
    setState(prev => ({ ...prev, status: 'processing' }))
    const productCategory = state.analysis?.productCategory ?? 'clothing'
    try {
      const result: TryOnResult = await generateTryOn(
        state.clothingFile!,
        state.selectedBackground!,
        null,
        state.detectedStyle,
        productCategory,
      )
      setState(prev => ({ ...prev, status: 'result', resultUrl: result.previewUrl, tryOnResult: result }))
    } catch {
      setState(prev => ({ ...prev, status: 'ready' }))
    }
  }, [state.clothingFile, state.selectedBackground, state.detectedStyle, state.analysis])

  const reset = useCallback(() => {
    if (state.clothingPreviewUrl) URL.revokeObjectURL(state.clothingPreviewUrl)
    setState({
      status: 'idle',
      modelPhotoFile: null,
      modelPhotoPreviewUrl: null,
      clothingFile: null,
      clothingPreviewUrl: null,
      detectedStyle: null,
      selectedBackground: null,
      resultUrl: null,
      tryOnResult: null,
      analysis: null,
    })
    setSuggestedBackgrounds([])
  }, [state.clothingPreviewUrl])

  return { state, suggestedBackgrounds, uploadClothing, selectBackground, selectStyle, generate, reset }
}
