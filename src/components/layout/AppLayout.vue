<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from './AppSidebar.vue'
import DashboardRightPanel from './DashboardRightPanel.vue'

const route = useRoute()
const showRightPanel = computed(() => route.name === 'Dashboard')
</script>

<template>
  <div class="flex h-screen min-h-0 overflow-hidden bg-[var(--color-surface-muted)]">
    <AppSidebar />

    <div class="flex min-w-0 flex-1 gap-6 p-6 pl-4">
      <main class="min-w-0 flex-1 overflow-y-auto">
        <RouterView v-slot="{ Component, route: viewRoute }">
          <Transition name="fade" mode="out-in">
            <KeepAlive :include="['Dashboard']">
              <component :is="Component" :key="viewRoute.name" />
            </KeepAlive>
          </Transition>
        </RouterView>
      </main>

      <DashboardRightPanel v-if="showRightPanel" class="hidden w-[300px] shrink-0 lg:flex" />
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}
</style>
