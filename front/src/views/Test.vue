<template>
    <h1>Total price: {{ store.sumPrice }}</h1>
    <h1>test counts: {{ store.count }}</h1>
    <h1>test counts2: {{ count }}</h1>
    <button @click="handlecnt">add</button>
    <button @click="togglestate">change</button>
    <button @click="resetState">Reset</button>
    <button @click="get_recommend">GetToken</button>
    <el-input size="large" v-model="username" placeholder="账号" class="input"></el-input>
    <el-input size="large" v-model="password" placeholder="密码" class="input"></el-input>
    <el-button type="primary" @click="store.getToken(username, password)">查询</el-button>
    <h3>{{ data.top_list }}</h3>
    <!-- <ul>
        <li v-for="item in ">
            {{ item }}
        </li>
    </ul> -->
</template>

<script lang="ts" setup>
import { reactive, ref } from 'vue'
import { useStore } from "../store/index";
import { storeToRefs } from "pinia" //将变量变成响应式
import { get_stocks } from "../api/index.js"
const username = ref('')
const password = ref('')
const data = reactive({
    top_list:[]
})
const store = useStore();
let { count } = storeToRefs(store)
const handlecnt=() => {
    store.count++;
    count.value++;
}
function togglestate() {
    store.$state = {
        count: 100,
        list:[{
            name:"huawei",
                price:5299,
                num:2
        },{
            name:"xiaomi",
            price:4999,
            num:1
        }],
        token:[]
    }
}
//重置状态
function resetState() {
    store.$reset();
}
//监听整个仓库变化
store.$subscribe((mutation, state)=>{
        console.log("mutation:", mutation)
        console.log("state:", state)
    })
function get_recommend() {
    get_stocks("储能").then((res)=>{
        console.log(res.data)
        data.top_list = res.data
    })
    console.log(data)
}


</script>

<style lang="scss" scoped>

</style>