var path = require('path')

export default {
  // "resolve":{
	// 	alias:{
	// 		utils: path.resolve(__dirname, 'src/utils/'),
	// 	}
	// },
  "proxy": {
    "/api": {
      "target": "http://jsonplaceholder.typicode.com/",
      "changeOrigin": true,
      "pathRewrite": { "^/api" : "" }
    }
  },
}
