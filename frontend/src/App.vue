<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const API = 'https://orange-space-guacamole-69g74r5pq574f5w6-8000.app.github.dev'

const grades = ref([])
const newTeacher = ref('')
const newSubject = ref('')
const newGrade1 = ref(null)
const newGrade2 = ref(null)
const newGrade3 = ref(null)

const editingId = ref(null)
const editTeacher = ref('')
const editSubject = ref('')
const editGrade1 = ref(null)
const editGrade2 = ref(null)
const editGrade3 = ref(null)

onMounted(async () => {
  try {
    const { data } = await axios.get(`${API}/grades`)
    // Защита: если data не массив — ставим пустой массив
    grades.value = Array.isArray(data) ? data : []
  } catch (e) {
    console.error('Ошибка загрузки:', e)
    grades.value = []
  }
})

// Общий средний — только по строкам, где avg не null
const totalAvg = computed(() => {
  if (!Array.isArray(grades.value) || grades.value.length === 0) return '—'
  const withAvg = grades.value.filter(g => g.avg !== null)
  if (withAvg.length === 0) return '—'
  const sum = withAvg.reduce((acc, g) => acc + g.avg, 0)
  return (sum / withAvg.length).toFixed(2)
})

function fmt(v) {
  return v === null || v === undefined ? '—' : v
}

function resetForm() {
  newTeacher.value = ''
  newSubject.value = ''
  newGrade1.value = null
  newGrade2.value = null
  newGrade3.value = null
}

async function addGrade() {
  if (!newTeacher.value.trim() || !newSubject.value.trim()) return

  try {
    const { data } = await axios.post(`${API}/grades`, {
      teacher: newTeacher.value,
      subject: newSubject.value,
      grade1: newGrade1.value,
      grade2: newGrade2.value,
      grade3: newGrade3.value
    })
    grades.value.push(data)
    resetForm()
  } catch (e) {
    console.error('Ошибка добавления:', e)
  }
}

function startEdit(item) {
  editingId.value = item.id
  editTeacher.value = item.teacher
  editSubject.value = item.subject
  editGrade1.value = item.grade1
  editGrade2.value = item.grade2
  editGrade3.value = item.grade3
}

async function saveEdit() {
  try {
    const { data } = await axios.put(`${API}/grades/${editingId.value}`, {
      teacher: editTeacher.value,
      subject: editSubject.value,
      grade1: editGrade1.value,
      grade2: editGrade2.value,
      grade3: editGrade3.value
    })
    const item = grades.value.find(g => g.id === editingId.value)
    if (item) Object.assign(item, data)
    editingId.value = null
  } catch (e) {
    console.error('Ошибка обновления:', e)
  }
}

async function deleteGrade(id) {
  try {
    await axios.delete(`${API}/grades/${id}`)
    grades.value = grades.value.filter(g => g.id !== id)
  } catch (e) {
    console.error('Ошибка удаления:', e)
  }
}
</script>

<template>
  <div style="max-width: 950px; margin: 30px auto; font-family: sans-serif;">
    <h1>Оценки за ЛЭС</h1>

    <!-- Форма добавления -->
    <div style="display: flex; gap: 6px; margin-bottom: 15px; flex-wrap: wrap; align-items: center;">
      <input v-model="newTeacher" placeholder="ФИО преподавателя" style="width: 160px; padding: 6px;" />
      <input v-model="newSubject" placeholder="Предмет" style="width: 130px; padding: 6px;" />

      <select v-model.number="newGrade1" style="width: 60px; padding: 6px;">
        <option :value="null">—</option>
        <option :value="3">3</option>
        <option :value="4">4</option>
        <option :value="5">5</option>
      </select>

      <select v-model.number="newGrade2" style="width: 60px; padding: 6px;">
        <option :value="null">—</option>
        <option :value="3">3</option>
        <option :value="4">4</option>
        <option :value="5">5</option>
      </select>

      <select v-model.number="newGrade3" style="width: 60px; padding: 6px;">
        <option :value="null">—</option>
        <option :value="3">3</option>
        <option :value="4">4</option>
        <option :value="5">5</option>
      </select>

      <button @click="addGrade" style="padding: 6px 14px;">Добавить</button>
    </div>

    <!-- Таблица -->
    <table border="1" cellpadding="6" style="width: 100%; border-collapse: collapse; text-align: center;">
      <thead>
        <tr style="background: #f0f0f0;">
          <th>ФИО преподавателя</th>
          <th>Предмет</th>
          <th>Оценка 1</th>
          <th>Оценка 2</th>
          <th>Оценка 3</th>
          <th>Средний балл</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in grades" :key="item.id">
          <template v-if="editingId === item.id">
            <td><input v-model="editTeacher" style="width: 140px;" /></td>
            <td><input v-model="editSubject" style="width: 110px;" /></td>

            <td>
              <select v-model.number="editGrade1" style="width: 55px;">
                <option :value="null">—</option>
                <option :value="3">3</option>
                <option :value="4">4</option>
                <option :value="5">5</option>
              </select>
            </td>
            <td>
              <select v-model.number="editGrade2" style="width: 55px;">
                <option :value="null">—</option>
                <option :value="3">3</option>
                <option :value="4">4</option>
                <option :value="5">5</option>
              </select>
            </td>
            <td>
              <select v-model.number="editGrade3" style="width: 55px;">
                <option :value="null">—</option>
                <option :value="3">3</option>
                <option :value="4">4</option>
                <option :value="5">5</option>
              </select>
            </td>

            <td>{{ fmt(item.avg) }}</td>
            <td>
              <button @click="saveEdit">💾</button>
              <button @click="editingId = null">Отмена</button>
            </td>
          </template>

          <template v-else>
            <td>{{ item.teacher }}</td>
            <td>{{ item.subject }}</td>
            <td>{{ fmt(item.grade1) }}</td>
            <td>{{ fmt(item.grade2) }}</td>
            <td>{{ fmt(item.grade3) }}</td>
            <td><strong>{{ fmt(item.avg) }}</strong></td>
            <td>
              <button @click="startEdit(item)">✏️</button>
              <button @click="deleteGrade(item.id)">🗑️</button>
            </td>
          </template>
        </tr>

        <tr v-if="grades.length === 0">
          <td colspan="7" style="color: gray;">Пусто. Добавь первый предмет.</td>
        </tr>
      </tbody>
    </table>

    <div style="margin-top: 15px; text-align: right; font-size: 18px;" v-if="grades.length > 0">
      <strong>Общий средний балл: {{ totalAvg }}</strong>
    </div>
  </div>
</template>