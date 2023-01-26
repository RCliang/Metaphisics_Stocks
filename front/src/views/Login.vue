<template>
    <div class="login-panel">
        <el-card class="box-card">
            <template #header>
                <div class="card-header">
                    <span>Login</span>
                </div>
            </template>
            <el-form ref="ruleFormRef" :model="ruleForm" status-icon :rules="rules" label-width="120px" class="demo-ruleForm" @keyup.enter="submitForm(ruleFormRef)">
                <el-form-item label="UserID" prop="userID">
                    <el-input v-model="ruleForm.userID" type="UserID" autocomplete="off" />
                </el-form-item>
                <el-form-item label="PassWord" prop="pass">
                    <el-input v-model="ruleForm.pass" type="password" autocomplete="off" />
                </el-form-item>
                <el-form-item label="remember me" prop="rememberme">
                    <el-checkbox label="Yes" name="type" />
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="submitForm(ruleFormRef)">Login</el-button>
                    <el-button @click="resetForm(ruleFormRef)">Reset</el-button>
                </el-form-item>
            </el-form>
        </el-card>
    </div>
</template>

<script lang="ts" setup>

import { reactive, ref,inject } from 'vue'
import type { FormInstance } from 'element-plus'
import {useRouter} from 'vue-router'
import { login, get_stocks } from '../api/index.js'

const router = useRouter()


const ruleFormRef = ref<FormInstance>()

//表单中需传递给后端的数据
const ruleForm = reactive({
    userID: '',
    pass: '',
    rememberme: false,
})

const rules = reactive({
    userID: [
        { required: true, message: 'Please input ID', trigger: 'blur' },
        { min: 3, max: 10, message: 'Length should be 3 to 5', trigger: 'blur' },
    ],
    pass: [
        { required: true, message: 'Please input password', trigger: 'blur' },
        { min: 4, max: 12, message: 'Length should be 4 to 12', trigger: 'blur' },
    ],
})

const submitForm = (formEl: FormInstance | undefined) => {
    if (!formEl) return
    formEl.validate((valid) => {
        if (valid) {
            console.log(ruleForm.userID)
            console.log(ruleForm.pass)
            login(ruleForm.userID, ruleForm.pass).then((res) => {
                console.log(res.data)})
            router.push("/performance")
        } else {
            console.log('error submit!')
            return false
        }
    })
}

const resetForm = (formEl: FormInstance | undefined) => {
    if (!formEl) return
    formEl.resetFields()
}
</script>


<style lang="scss" scoped>
.login-panel {
    width: 500px;
    margin: 0 auto;
    margin-top: 130px;

}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.text {
    font-size: 14px;
}

.item {
    margin-bottom: 18px;
}

.box-card {
    width: 480px;
}
</style>