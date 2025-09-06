#!/bin/bash

# 设置基础目录
BASE_DIR="/mnt/data/cn/workflow/aiida-abacus/examples/ORB"
ORB_DIR="${BASE_DIR}/apns-orbitals-precision-v1"
PSEUDO_DIR="${BASE_DIR}/apns-pseudopotentials-v1"

# 在当前目录下创建临时目录结构
IMPORT_DIR="./apns-import"
rm -rf "${IMPORT_DIR}"  # 清除之前可能存在的旧目录
mkdir -p "${IMPORT_DIR}/Pseudopotential"
mkdir -p "${IMPORT_DIR}/Orbitals"

echo "源轨道目录: ${ORB_DIR}"
echo "源赝势目录: ${PSEUDO_DIR}"
echo "目标导入目录: ${IMPORT_DIR}"

# 1. 创建轨道文件链接
cd "${ORB_DIR}" || { echo "无法进入轨道目录: ${ORB_DIR}"; exit 1; }
echo "正在处理轨道文件..."
for file in *.orb; do
    # 提取元素符号（文件名第一部分）
    element=$(echo "$file" | cut -d'_' -f1)
    target_dir="${IMPORT_DIR}/Orbitals/${element}_dzp"
    mkdir -p "$target_dir"
    
    # 目标文件路径
    target_path="${target_dir}/${file}"
    
    # 如果文件已存在，删除它
    if [ -e "${target_path}" ]; then
        rm -f "${target_path}"
    fi
    
    # 创建符号链接
    ln -s "$(pwd)/${file}" "${target_path}" && \
        echo "创建轨道链接: ${file} -> ${target_path}" || \
        echo "警告: 无法创建轨道链接: ${file} -> ${target_path}"
done

# 2. 创建赝势文件链接 - 处理混合命名
cd "${PSEUDO_DIR}" || { echo "无法进入赝势目录: ${PSEUDO_DIR}"; exit 1; }
echo "正在处理赝势文件..."
for pseudo in *.upf; do
    # 提取元素符号（文件名第一部分）
    element=$(echo "$pseudo" | cut -d'_' -f1)
    
    # 特殊处理：有些文件以元素开头但包含更多信息
    # 检查提取的元素是否是有效的化学符号
    if [[ "$element" =~ ^[A-Z][a-z]?$ ]]; then
        # 有效元素符号
        target_link="${IMPORT_DIR}/Pseudopotential/${element}.upf"
    else
        # 尝试从文件名开头提取元素符号
        element=$(echo "$pseudo" | sed 's/\.upf$//')
    fi
    
    # 再次验证元素符号
    if [[ "$element" =~ ^[A-Z][a-z]?$ ]]; then
        # 如果文件已存在，删除它
        if [ -e "${target_link}" ]; then
            rm -f "${target_link}"
        fi
        
        # 创建符号链接
        ln -s "$(pwd)/${pseudo}" "${target_link}" && \
            echo "创建赝势链接: ${pseudo} -> ${target_link}" || \
            echo "警告: 无法创建赝势链接: ${pseudo} -> ${target_link}"
    else
        echo "错误: 无法从文件名提取元素符号: $pseudo"
        echo "请手动处理此文件"
    fi
done

# 3. 验证结果
echo ""
echo "===== 导入结果验证 ====="
echo "临时目录结构已创建在: ${IMPORT_DIR}"
echo "轨道文件数: $(find ${IMPORT_DIR}/Orbitals -name "*.orb" | wc -l)"
echo "赝势文件数: $(find ${IMPORT_DIR}/Pseudopotential -name "*.upf" | wc -l)"
echo ""
echo "目录结构:"
tree -L 3 "${IMPORT_DIR}" | head -20