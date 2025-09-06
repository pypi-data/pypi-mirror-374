#!/bin/bash

# 设置基础目录 - 使用当前目录作为基准
BASE_DIR="$(pwd)/ORB"
ORB_DIR="${BASE_DIR}/apns-orbitals-precision-v1"
PSEUDO_DIR="${BASE_DIR}/apns-pseudopotentials-v1"

# 创建目标目录结构
IMPORT_DIR="$(pwd)/apns-import"
rm -rf "${IMPORT_DIR}"  # 清除旧目录
mkdir -p "${IMPORT_DIR}/Orbitals"
mkdir -p "${IMPORT_DIR}/Pseudopotential"

echo "当前工作目录: $(pwd)"
echo "源轨道目录: ${ORB_DIR}"
echo "源赝势目录: ${PSEUDO_DIR}"
echo "目标导入目录: ${IMPORT_DIR}"

# 验证目录是否存在
if [ ! -d "${ORB_DIR}" ]; then
    echo "错误: 轨道目录不存在: ${ORB_DIR}"
    exit 1
fi

if [ ! -d "${PSEUDO_DIR}" ]; then
    echo "错误: 赝势目录不存在: ${PSEUDO_DIR}"
    exit 1
fi

# 1. 复制轨道文件
echo "正在复制轨道文件..."
cd "${ORB_DIR}" || exit
for file in *.orb; do
    # 提取元素符号（文件名第一部分）
    element=$(echo "$file" | cut -d'_' -f1)
    target_dir="${IMPORT_DIR}/Orbitals/${element}_dzp"
    mkdir -p "$target_dir"
    
    # 复制文件
    cp -v "$file" "${target_dir}/"
done

# 2. 复制赝势文件
echo "正在复制赝势文件..."
cd "${PSEUDO_DIR}" || exit
for pseudo in *.upf *.UPF; do
    # 提取元素符号（文件名第一部分）
    element=$(echo "$pseudo" | cut -d'_' -f1 | cut -d'.' -f1)
    
    # 特殊处理：有些文件以元素开头但包含更多信息
    # 检查提取的元素是否是有效的化学符号
    if [[ "$element" =~ ^[A-Z][a-z]?$ ]]; then
        # 有效元素符号
        target_file="${IMPORT_DIR}/Pseudopotential/${element}.upf"
    else
        # 尝试从文件名开头提取元素符号
        element=$(echo "$pseudo" | sed 's/[._].*$//')
        target_file="${IMPORT_DIR}/Pseudopotential/${element}.upf"
    fi
    
    # 复制文件
    cp -v "$pseudo" "${target_file}"
done

# 3. 验证结果
echo ""
echo "===== 复制结果 ====="
echo "轨道文件数: $(find "${IMPORT_DIR}/Orbitals" -name "*.orb" | wc -l)"
echo "赝势文件数: $(find "${IMPORT_DIR}/Pseudopotential" -name "*.upf" | wc -l)"
echo ""
echo "目录结构预览:"
tree -L 3 "${IMPORT_DIR}" | head -20