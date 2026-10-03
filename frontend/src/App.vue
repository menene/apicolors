<script setup>
import { nextTick, onBeforeUnmount, ref } from "vue";

const MAX_FILE_SIZE = 5 * 1024 * 1024;
const ALLOWED_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);

const fileInput = ref(null);
const resultsElement = ref(null);
const selectedFile = ref(null);
const previewUrl = ref("");
const colorCount = ref(5);
const palette = ref(null);
const errorMessage = ref("");
const isDragging = ref(false);
const isLoading = ref(false);
const copiedColor = ref("");
const isDark = ref(localStorage.getItem("apicolors-theme") === "dark");

function applyTheme() {
  document.documentElement.dataset.theme = isDark.value ? "dark" : "light";
}

function toggleTheme() {
  isDark.value = !isDark.value;
  localStorage.setItem("apicolors-theme", isDark.value ? "dark" : "light");
  applyTheme();
}

function selectFile(file) {
  errorMessage.value = "";
  if (!file) return;
  if (!ALLOWED_TYPES.has(file.type)) {
    errorMessage.value = "Selecciona una imagen JPEG, PNG o WebP.";
    return;
  }
  if (file.size > MAX_FILE_SIZE) {
    errorMessage.value = "La imagen supera el límite de 5 MB.";
    return;
  }

  releasePreview();
  selectedFile.value = file;
  previewUrl.value = URL.createObjectURL(file);
  palette.value = null;
}

function onFileChange(event) {
  selectFile(event.target.files?.[0]);
}

function onDrop(event) {
  isDragging.value = false;
  selectFile(event.dataTransfer?.files?.[0]);
}

async function analyzeImage() {
  if (!selectedFile.value || isLoading.value) return;

  isLoading.value = true;
  errorMessage.value = "";
  try {
    const formData = new FormData();
    formData.append("image", selectedFile.value);
    formData.append("color_count", String(colorCount.value));

    const response = await fetch("/api/v1/palettes", {
      method: "POST",
      body: formData,
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(
        payload.error?.message || "No fue posible analizar la imagen.",
      );
    }

    palette.value = payload;
    await nextTick();
    resultsElement.value?.scrollIntoView({
      behavior: "smooth",
      block: "nearest",
    });
  } catch (error) {
    errorMessage.value =
      error instanceof Error
        ? error.message
        : "No fue posible conectar con la API.";
  } finally {
    isLoading.value = false;
  }
}

async function copyColor(hex) {
  try {
    await navigator.clipboard.writeText(hex);
  } catch {
    const textarea = document.createElement("textarea");
    textarea.value = hex;
    document.body.append(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
  }
  copiedColor.value = hex;
  window.setTimeout(() => {
    if (copiedColor.value === hex) copiedColor.value = "";
  }, 1200);
}

function releasePreview() {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
  previewUrl.value = "";
}

function reset() {
  releasePreview();
  selectedFile.value = null;
  palette.value = null;
  errorMessage.value = "";
  copiedColor.value = "";
  if (fileInput.value) fileInput.value.value = "";
  fileInput.value?.focus();
}

applyTheme();
onBeforeUnmount(releasePreview);
</script>

<template>
  <nav class="topbar" aria-label="Navegación principal">
    <div class="wrap nav">
      <a class="brand" href="/" aria-label="API a todo color, inicio">
        <span class="brand-mark" aria-hidden="true"><i /><i /><i /><i /></span>
        API a todo color
      </a>
      <div class="nav-actions">
        <a href="/docs">
          <i class="fa-solid fa-book" aria-hidden="true" /> API Docs
        </a>
        <a href="https://github.com/menene/apicolors">
          <i class="fa-brands fa-github" aria-hidden="true" /> GitHub
        </a>
        <button
          class="theme-toggle"
          type="button"
          :aria-label="isDark ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'"
          @click="toggleTheme"
        >
          <i
            :class="isDark ? 'fa-solid fa-sun' : 'fa-solid fa-moon'"
            aria-hidden="true"
          />
        </button>
      </div>
    </div>
  </nav>

  <main class="app-shell">
    <header class="hero">
      <div>
        <p class="eyebrow">Analizador de color</p>
        <h1>Extrae una paleta de una imagen</h1>
        <p>
          Selecciona una imagen y define entre 3 y 8 colores. La API devuelve
          los colores dominantes con sus valores HEX, RGB y porcentajes.
        </p>
      </div>
      <div class="technology-list" aria-label="Tecnologías">
        <span>
          <img
            src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/vuejs/vuejs-original.svg"
            alt=""
          >
          Vue 3
        </span>
        <span>
          <img
            src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/fastapi/fastapi-original.svg"
            alt=""
          >
          FastAPI
        </span>
        <span>
          <img
            src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg"
            alt=""
          >
          Python
        </span>
      </div>
    </header>

    <section
      class="workspace"
      aria-label="Analizador de colores"
      :aria-busy="isLoading"
    >
      <div class="controls-panel">
        <div class="panel-heading">
          <span class="step-number">01</span>
          <div>
            <h2>Configura el análisis</h2>
            <p>Imagen y cantidad de colores.</p>
          </div>
        </div>

        <label
          class="drop-zone"
          :class="{ 'is-dragging': isDragging, 'has-file': selectedFile }"
          for="image-input"
          @dragenter.prevent="isDragging = true"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="onDrop"
        >
          <i class="upload-icon fa-solid fa-cloud-arrow-up" aria-hidden="true" />
          <strong>
            {{ selectedFile ? selectedFile.name : "Selecciona una imagen" }}
          </strong>
          <span>
            {{
              selectedFile
                ? "Haz clic para reemplazarla"
                : "Haz clic o arrastra el archivo aquí"
            }}
          </span>
          <small>JPEG, PNG o WebP · máximo 5 MB</small>
        </label>
        <input
          id="image-input"
          ref="fileInput"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          hidden
          @change="onFileChange"
        >

        <div class="range-control">
          <label for="color-count">
            Cantidad de colores <output>{{ colorCount }}</output>
          </label>
          <input
            id="color-count"
            v-model.number="colorCount"
            type="range"
            min="3"
            max="8"
          >
          <div class="range-labels"><span>3</span><span>8</span></div>
        </div>
        <button
          class="primary-button"
          type="button"
          :disabled="!selectedFile || isLoading"
          @click="analyzeImage"
        >
          <i
            :class="
              isLoading
                ? 'fa-solid fa-circle-notch fa-spin'
                : 'fa-solid fa-wand-magic-sparkles'
            "
            aria-hidden="true"
          />
          {{ isLoading ? "Analizando" : "Extraer colores" }}
        </button>
        <p v-if="errorMessage" class="error-message" role="alert">
          <i class="fa-solid fa-circle-exclamation" aria-hidden="true" />
          {{ errorMessage }}
        </p>
      </div>

      <div class="preview-panel">
        <div class="panel-heading preview-heading">
          <span class="step-number">02</span>
          <div>
            <h2>Vista previa</h2>
            <p>
              {{
                previewUrl
                  ? "Imagen lista para procesar."
                  : "Selecciona una imagen para continuar."
              }}
            </p>
          </div>
        </div>
        <div class="preview-content">
          <div v-if="!previewUrl" class="empty-preview">
            <i class="fa-regular fa-image" aria-hidden="true" />
            <span>Sin imagen seleccionada</span>
          </div>
          <img
            v-else
            :src="previewUrl"
            alt="Vista previa de la imagen seleccionada"
          >
        </div>
      </div>
    </section>

    <section
      v-if="palette"
      ref="resultsElement"
      class="results"
      aria-live="polite"
    >
      <div class="results-heading">
        <div class="panel-heading">
          <span class="step-number">03</span>
          <div>
            <h2>Paleta extraída</h2>
            <p>{{ palette.color_count }} colores ordenados por frecuencia.</p>
          </div>
        </div>
        <button class="secondary-button" type="button" @click="reset">
          <i class="fa-solid fa-rotate-left" aria-hidden="true" />
          Nueva imagen
        </button>
      </div>
      <div class="palette-bar" aria-label="Distribución de la paleta">
        <div
          v-for="color in palette.colors"
          :key="color.hex"
          :title="`${color.hex} · ${color.percentage}%`"
          :style="{
            backgroundColor: color.hex,
            flexGrow: color.percentage,
          }"
        />
      </div>
      <div class="color-list">
        <article
          v-for="color in palette.colors"
          :key="color.hex"
          class="color-card"
        >
          <div class="swatch" :style="{ backgroundColor: color.hex }" />
          <div class="color-info">
            <strong>{{ color.hex }}</strong>
            <span>
              RGB({{ color.rgb.red }}, {{ color.rgb.green }},
              {{ color.rgb.blue }})
            </span>
          </div>
          <div class="percent">{{ color.percentage }}%</div>
          <button
            class="copy-button"
            type="button"
            :aria-label="`Copiar ${color.hex}`"
            @click="copyColor(color.hex)"
          >
            <i
              :class="
                copiedColor === color.hex
                  ? 'fa-solid fa-check'
                  : 'fa-regular fa-copy'
              "
              aria-hidden="true"
            />
            {{ copiedColor === color.hex ? "Copiado" : "Copiar" }}
          </button>
        </article>
      </div>
      <p class="metadata">
        <i class="fa-regular fa-file-image" aria-hidden="true" />
        {{ palette.filename }} · {{ palette.width }} × {{ palette.height }} px ·
        {{ palette.processing_ms }} ms
      </p>
    </section>
  </main>

  <footer>
    <div class="wrap footer-row">
      <span>Vue 3 + FastAPI + Docker</span>
      <a href="https://github.com/menene/apicolors">Código fuente</a>
    </div>
  </footer>
</template>
