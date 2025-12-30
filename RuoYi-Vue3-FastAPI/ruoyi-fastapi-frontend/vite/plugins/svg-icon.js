import path from 'path'
import { createRequire } from 'module'

const require = createRequire(import.meta.url)

export default function createSvgIcon(isBuild) {
    // 使用 require 来兼容 CommonJS 模块
    const { createSvgIconsPlugin } = require('vite-plugin-svg-icons')
    
    return createSvgIconsPlugin({
		iconDirs: [path.resolve(process.cwd(), 'src/assets/icons/svg')],
        symbolId: 'icon-[dir]-[name]',
        svgoOptions: isBuild
    })
}
