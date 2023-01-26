import request from '../utils/http.js'
// import store from "../store"

// export function fetchPermission() {
//     return axios.get("/api/permission?user=" + store.state.UserToken);
// }

export function login(username, password) {
    return request.post("/jwt/token", {
        "username": username,
        "password": password
    }, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            "WWW-Authenticate": "Bearer"
        }
    }
    )
}

export async function get_stocks(plate_name) {
    return await request.get("/long_small/" + plate_name)
}