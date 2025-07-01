
/**
 * Form component to create a new product with an optional custom prompt.
 *
 * On submit, calls the createProduct hook and navigates to the product page.
 */
import React, { useState } from 'react'
import { useRouter } from 'next/router'
import { useCreateProduct } from '@/utils/api'

export default function NewProductForm() {
  const router = useRouter()
  const [nameText, setNameText] = useState('')
  const [promptText, setPromptText] = useState('')
  const [submitError, setSubmitError] = useState<string | null>(null)
  const { mutateAsync: createProduct, isLoading } = useCreateProduct()

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setSubmitError(null)
    try {
      const result = await createProduct({ name: nameText, prompt: promptText })
      router.push(`/products/${result.id}`)
    } catch (error: any) {
      setSubmitError(error.message || 'An error occurred')
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="flex flex-col sm:flex-row items-center gap-2">
        <input
          type="text"
          placeholder="Enter product name…"
          value={nameText}
          onChange={(e) => setNameText(e.target.value)}
          className="bg-gray-800 text-white placeholder-gray-500 border border-gray-700 rounded px-4 py-2 flex-1"
        />
        <input
          type="text"
          placeholder="Enter shopping prompt…"
          value={promptText}
          onChange={(e) => setPromptText(e.target.value)}
          className="bg-gray-800 text-white placeholder-gray-500 border border-gray-700 rounded px-4 py-2 flex-1"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded px-4 py-2"
        >
          {isLoading ? 'Loading...' : 'Go'}
        </button>
      </div>
      {submitError && <p className="text-red-400 mt-2">{submitError}</p>}
    </form>
  )
}