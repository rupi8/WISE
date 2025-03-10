#!/bin/bash
# 当 static_lib 的版本更新后可以使用这个脚本将更新后的 static_lib 打包然后上传。

cd ../static_lib
version=$(cat version)
tar zcvf ../static_lib_${version}.tar.gz .
cd ..
ossutil cp static_lib_${version}.tar.gz oss://m5stack/resource/linux/llm/static_lib_${version}.tar.gz


