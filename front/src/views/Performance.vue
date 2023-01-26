<script setup>
import {get_stocks} from '../api'
import { defineComponent, ref, reactive } from 'vue'
const input = ref('')
const store = reactive({
    tableData:[]
})
function query() {
    get_stocks(input.value).then((res)=>{
        console.log(res.data)
        store.tableData = []
        for (let key in res.data) {
            store.tableData.push(
                {
                    "code": key,
                    "name": res.data[key]
                }
            )
        }
        console.log(store.tableData)
    })
}


</script>

<template>
    <h2>板块查询</h2>
    <el-input size="large" v-model="input" placeholder="请输入内容" class="input"></el-input>
    <el-button type="primary" @click="query">查询</el-button>
    <el-table :data="store.tableData" style="width: 100%">
    <el-table-column prop="code" label="代码" width="180"> </el-table-column>
    <el-table-column prop="name" label="名字" width="180"> </el-table-column>
  </el-table>
</template>

<style scoped>
.input{
    width: 200px;
    margin-right: 50px;
}
</style>
