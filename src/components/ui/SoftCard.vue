<script setup>
defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  padding: { type: String, default: 'p-6 md:p-8' },
  hoverable: { type: Boolean, default: false },
  class: { type: String, default: '' },
})
</script>

<template>
  <section
    class="soft-card"
    :class="[padding, hoverable ? 'soft-card-hover' : '', $props.class]"
  >
    <header v-if="title || $slots.header" class="mb-5 flex items-start justify-between gap-4">
      <div>
        <h3 v-if="title" class="text-lg font-semibold tracking-tight text-slate-800">
          {{ title }}
        </h3>
        <p v-if="subtitle" class="mt-1 text-sm text-slate-400">{{ subtitle }}</p>
      </div>
      <slot name="header" />
    </header>
    <slot />
  </section>
</template>
