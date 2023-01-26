import { defineStore } from 'pinia'
import { login, get_stocks } from '../api/index.js'
export const useStore = defineStore('main', {
    // other options...
    state: ()=>{
        return {
            count: 10,
            list:[{
                name:"iphone",
                price:5699,
                num:1
        },{
            name:"xiaomi",
            price:4999,
            num:3
        }],
        token:[]
        }
    },
    getters: {
        sumPrice:(state)=>{
            return state.list.reduce((pre,item)=>{
                return pre + (item.price*item.num)
            },0)
        }
    },
    actions:{
        getToken(username, password){
            let result = login(username, password)
            console.log(result.data)
            this.token.push(result.data);
        }
    }
  })