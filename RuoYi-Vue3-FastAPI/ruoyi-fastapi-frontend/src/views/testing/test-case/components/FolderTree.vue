<template>
  <el-card class="folder-tree-card">
    <template #header>
      <div class="tree-header">
        <span class="title">文件夹</span>
        <div class="actions">
          <el-button type="primary" size="small" :icon="Plus" @click="handleAddFolder" v-hasPermi="['testing:folder:add']">新建</el-button>
          <el-button size="small" :icon="Refresh" @click="loadFolderTree" />
        </div>
      </div>
    </template>

    <div class="tree-container">
      <!-- 全部用例节点 -->
      <div
        class="tree-item all-cases"
        :class="{ active: selectedFolderId === null }"
        @click="handleSelectAll"
      >
        <el-icon><FolderOpened /></el-icon>
        <span>全部用例</span>
      </div>

      <!-- 文件夹树 -->
      <el-tree
        ref="treeRef"
        :data="folderTree"
        :props="treeProps"
        node-key="folder_id"
        :expand-on-click-node="false"
        :highlight-current="true"
        :current-node-key="selectedFolderId"
        @node-click="handleNodeClick"
        @node-contextmenu="handleContextMenu"
        empty-text="暂无文件夹"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <el-icon><Folder /></el-icon>
            <span class="folder-name">{{ data.folder_name }}</span>
            <span class="case-count" v-if="data.case_count > 0">({{ data.case_count }})</span>
          </div>
        </template>
      </el-tree>
    </div>

    <!-- 右键菜单 -->
    <div
      v-show="contextMenuVisible"
      class="context-menu"
      :style="{ top: contextMenuY + 'px', left: contextMenuX + 'px' }"
    >
      <div class="menu-item" @click="handleAddSubFolder">
        <el-icon><FolderAdd /></el-icon>
        新建子文件夹
      </div>
      <div class="menu-item" @click="handleEditFolder">
        <el-icon><Edit /></el-icon>
        编辑
      </div>
      <div class="menu-item danger" @click="handleDeleteFolder">
        <el-icon><Delete /></el-icon>
        删除
      </div>
    </div>

    <!-- 新建/编辑文件夹对话框 -->
    <el-dialog
      v-model="folderDialogVisible"
      :title="folderForm.folderId ? '编辑文件夹' : '新建文件夹'"
      width="450px"
      append-to-body
      @close="resetFolderForm"
    >
      <el-form ref="folderFormRef" :model="folderForm" :rules="folderRules" label-width="80px">
        <el-form-item label="文件夹名" prop="folderName">
          <el-input v-model="folderForm.folderName" placeholder="请输入文件夹名称" maxlength="100" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="folderForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="folderDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitFolderForm">确定</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, reactive, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Folder, FolderOpened, FolderAdd, Edit, Delete } from '@element-plus/icons-vue'
import { getFolderTree, addFolder, updateFolder, delFolder } from '@/api/testing/folder'

const props = defineProps({
  projectId: {
    type: Number,
    default: null
  },
  selectedFolderId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['select', 'refresh'])

// 树形数据
const treeRef = ref(null)
const folderTree = ref([])
const treeProps = {
  label: 'folder_name',
  children: 'children'
}

// 右键菜单
const contextMenuVisible = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const contextNode = ref(null)

// 文件夹表单
const folderDialogVisible = ref(false)
const folderFormRef = ref(null)
const folderForm = reactive({
  folderId: null,
  parentId: null,
  folderName: '',
  description: ''
})

const folderRules = {
  folderName: [
    { required: true, message: '请输入文件夹名称', trigger: 'blur' },
    { max: 100, message: '长度不能超过100个字符', trigger: 'blur' }
  ]
}

// 加载文件夹树
const loadFolderTree = async () => {
  if (!props.projectId) {
    folderTree.value = []
    return
  }
  
  try {
    const res = await getFolderTree(props.projectId)
    folderTree.value = res.data || []
  } catch (error) {
    console.error('加载文件夹树失败:', error)
  }
}

// 选择全部
const handleSelectAll = () => {
  emit('select', null)
  if (treeRef.value) {
    treeRef.value.setCurrentKey(null)
  }
}

// 点击节点
const handleNodeClick = (data) => {
  emit('select', data.folder_id)
}

// 右键菜单
const handleContextMenu = (event, data) => {
  event.preventDefault()
  contextNode.value = data
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  contextMenuVisible.value = true
}

// 关闭右键菜单
const closeContextMenu = () => {
  contextMenuVisible.value = false
}

// 新建文件夹
const handleAddFolder = () => {
  resetFolderForm()
  folderDialogVisible.value = true
}

// 新建子文件夹
const handleAddSubFolder = () => {
  resetFolderForm()
  folderForm.parentId = contextNode.value?.folder_id
  folderDialogVisible.value = true
  closeContextMenu()
}

// 编辑文件夹
const handleEditFolder = () => {
  const folder = contextNode.value
  if (folder) {
    folderForm.folderId = folder.folder_id
    folderForm.folderName = folder.folder_name
    folderForm.description = folder.description
    folderDialogVisible.value = true
  }
  closeContextMenu()
}

// 删除文件夹
const handleDeleteFolder = async () => {
  const folder = contextNode.value
  closeContextMenu()
  
  if (!folder) return
  
  try {
    await ElMessageBox.confirm(
      `确认删除文件夹 "${folder.folder_name}" 吗？`,
      '警告',
      { type: 'warning' }
    )
    
    await delFolder(folder.folder_id)
    ElMessage.success('删除成功')
    loadFolderTree()
    emit('refresh')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error?.message || '删除失败')
    }
  }
}

// 重置表单
const resetFolderForm = () => {
  folderForm.folderId = null
  folderForm.parentId = null
  folderForm.folderName = ''
  folderForm.description = ''
  if (folderFormRef.value) {
    folderFormRef.value.resetFields()
  }
}

// 提交表单
const submitFolderForm = async () => {
  const valid = await folderFormRef.value?.validate()
  if (!valid) return
  
  try {
    if (folderForm.folderId) {
      await updateFolder(folderForm.folderId, {
        folderName: folderForm.folderName,
        description: folderForm.description
      })
      ElMessage.success('更新成功')
    } else {
      await addFolder({
        projectId: props.projectId,
        parentId: folderForm.parentId,
        folderName: folderForm.folderName,
        description: folderForm.description
      })
      ElMessage.success('创建成功')
    }
    
    folderDialogVisible.value = false
    loadFolderTree()
    emit('refresh')
  } catch (error) {
    ElMessage.error(error?.message || '操作失败')
  }
}

// 监听项目变化
watch(() => props.projectId, () => {
  loadFolderTree()
}, { immediate: true })

// 点击其他地方关闭右键菜单
onMounted(() => {
  document.addEventListener('click', closeContextMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', closeContextMenu)
})
</script>

<style scoped lang="scss">
.folder-tree-card {
  height: 100%;
  display: flex;
  flex-direction: column;

  .tree-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      font-weight: 600;
    }

    .actions {
      display: flex;
      gap: 8px;
    }
  }

  .tree-container {
    flex: 1;
    overflow: auto;

    .all-cases {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      cursor: pointer;
      border-radius: 4px;
      margin-bottom: 8px;
      background: #f5f7fa;

      &:hover {
        background: #e8f4ff;
      }

      &.active {
        background: #409eff;
        color: white;
      }
    }

    .tree-node {
      display: flex;
      align-items: center;
      gap: 6px;
      flex: 1;

      .folder-name {
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .case-count {
        color: #909399;
        font-size: 12px;
      }
    }
  }

  .context-menu {
    position: fixed;
    background: white;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    z-index: 3000;
    min-width: 150px;

    .menu-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px 16px;
      cursor: pointer;
      font-size: 14px;

      &:hover {
        background: #f5f7fa;
      }

      &.danger {
        color: #f56c6c;
      }
    }
  }
}

:deep(.el-card__header) {
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-card__body) {
  padding: 12px;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

:deep(.el-tree-node__content) {
  height: 32px;
  border-radius: 4px;
}

:deep(.el-tree-node.is-current > .el-tree-node__content) {
  background-color: #e8f4ff;
}
</style>

