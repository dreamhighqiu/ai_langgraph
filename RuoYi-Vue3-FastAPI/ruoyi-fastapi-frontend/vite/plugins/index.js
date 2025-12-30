import vue from '@vitejs/plugin-vue'

import createAutoImport from './auto-import'
// import createSvgIcon from './svg-icon'  // 临时禁用，Node.js 24不兼容
import createCompression from './compression'
import createSetupExtend from './setup-extend'

export default function createVitePlugins(viteEnv, isBuild = false) {
    const vitePlugins = [vue()]
    vitePlugins.push(createAutoImport())
	vitePlugins.push(createSetupExtend())
    // vitePlugins.push(createSvgIcon(isBuild))  // 临时禁用
	isBuild && vitePlugins.push(...createCompression(viteEnv))
    return vitePlugins
}
