let selectedProjectId = '';
let selectedRepo = '';
let selectedProjectName = '';
let selectedProjectDescription = ''
let selectedProjectVersionType = 'tag'; // 'tag' 或 'branch'
let selectedProjectVersion = '';
let currentStep = 1;

const projectGrid = document.getElementById('projectGrid');
const tagSelect = document.getElementById('tagSelect');
const branchSelect = document.getElementById('branchSelect');
const tagGroup = document.getElementById('tagGroup');
const branchGroup = document.getElementById('branchGroup');
const nextStep2Btn = document.querySelector('.step-content[data-step="2"] .next-step');
const prevStep2Btn = document.querySelector('.step-content[data-step="2"] .prev-step');
const prevStep3Btn = document.querySelector('.step-content[data-step="3"] .prev-step');
const progressFill = document.getElementById('progressFill');

// 更新已选择项目信息显示
async function updateSelectedProjectInfo() {
    const projectNameElement = document.getElementById('selectedProjectName');
    const projectDescElement = document.getElementById('selectedProjectDesc');
    const projectNameStep3Element = document.getElementById('selectedProjectNameStep3');
    const projectDescStep3Element = document.getElementById('selectedProjectDescStep3');
    const versionStep3Element = document.getElementById('selectedVersionStep3');


    if (projectNameElement) projectNameElement.textContent = selectedProjectName;
    if (projectDescElement) projectDescElement.textContent = selectedProjectDescription;

    if (projectNameStep3Element) projectNameStep3Element.textContent = selectedProjectName;
    if (projectDescStep3Element) projectDescStep3Element.textContent = selectedProjectDescription;
    if (versionStep3Element) versionStep3Element.textContent = selectedProjectVersion;
}

// 更新进度条
function updateProgress(step) {
    const progress = ((step - 1) / 2) * 100;
    progressFill.style.width = `${progress}%`;

    // 更新步骤指示器
    document.querySelectorAll('.step-indicator').forEach((indicator, index) => {
        indicator.classList.remove('active', 'completed');
        if (index + 1 < step) {
            indicator.classList.add('completed');
        } else if (index + 1 === step) {
            indicator.classList.add('active');
        }
    });
}

// 切换步骤
async function goToStep(step) {
    document.querySelectorAll('.step-content').forEach(el => el.classList.remove('active'));
    document.querySelector(`.step-content[data-step="${step}"]`).classList.add('active');
    currentStep = step;
    updateProgress(step);

    // 在进入第二步和第三步时更新项目信息
    if ((step === 2 || step === 3) && selectedRepo) {
        updateSelectedProjectInfo();
    }

    // 在进入第二步时加载版本信息
    if (step === 2 && selectedRepo) {
        await loadVersions(selectedRepo);
    }
}

// 加载项目列表并渲染按钮
async function loadProjects() {
    try {
        const res = await fetch('/api/projects');
        if (!res.ok) throw new Error('加载失败');
        const projects = await res.json();

        projectGrid.innerHTML = '';
        projects.forEach(p => {
            const card = document.createElement('div');
            card.className = 'project-card';
            card.dataset.repo = p.repo;

            card.innerHTML = `
                <div class="project-name">${p.name}</div>
                <div class="project-desc">${p.description}</div>
            `;

            card.addEventListener('click', () => {
                // 取消其他选中
                document.querySelectorAll('.project-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                selectedRepo = p.repo;
                selectedProjectName = p.name;
                selectedProjectDescription = p.description;
                selectedProjectId = p.id

                // 自动进入下一步
                setTimeout(() => {
                    goToStep(2);
                }, 300);
            });

            projectGrid.appendChild(card);
        });
    } catch (err) {
        projectGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #e74c3c;">
                <div style="font-size: 40px; margin-bottom: 15px;">⚠️</div>
                <div>❌ 加载项目失败</div>
                <div style="font-size: 14px; margin-top: 10px;">${err.message}</div>
            </div>
        `;
    }
}

// 加载版本信息（tag或branch）
async function loadVersions(repo) {
    if (selectedProjectVersionType === 'tag') {
        await loadTags(repo);
    } else {
        await loadBranches(repo);
    }
}

// 加载 Tags
async function loadTags(repo) {
    tagSelect.disabled = true;
    tagSelect.innerHTML = '';

    try {
        const res = await fetch(`/api/tags?project_id=${selectedProjectId}`);
        if (!res.ok) {
            let errorMsg = '获取版本信息失败';
            if (res.status === 404) {
                errorMsg = '项目不存在或无法访问';
            } else if (res.status === 403) {
                errorMsg = 'API访问限制，请稍后再试';
            } else if (res.status >= 500) {
                errorMsg = '服务器内部错误，请稍后重试';
            }
            throw new Error(errorMsg);
        }
        const tags = await res.json();

        // 直接展示有效选项，无需占位符
        let hasValidTags = false;

        if (tags.length > 0) {
            tags.slice(0, 30).forEach((tag, index) => {
                const opt = document.createElement('option');
                opt.value = tag.name;
                opt.textContent = tag.name;
                opt.style.color = '#2c3e50';

                tagSelect.appendChild(opt);

                // 默认选中第一个tag
                if (index === 0) {
                    tagSelect.value = tag.name;
                    nextStep2Btn.disabled = false;
                    hasValidTags = true;
                }
            });
        } else {
            // 无可用标签时不显示任何选项
            nextStep2Btn.disabled = true;
        }

        // 更新下一步按钮状态
        nextStep2Btn.disabled = !hasValidTags;
    } catch (err) {
        // 错误状态下提供友好提示
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = '加载失败，请重试';
        opt.disabled = true;
        opt.style.color = '#dc3545';
        tagSelect.appendChild(opt);
        nextStep2Btn.disabled = true;

        // 提供更友好的错误信息
        let userFriendlyMessage = err.message;
        if (err.message.includes('fetch')) {
            userFriendlyMessage = '网络连接异常，请检查网络后重试';
        } else if (err.message.includes('Failed to fetch')) {
            userFriendlyMessage = '无法连接到服务器，请稍后重试';
        }

        showError('获取Tag失败', userFriendlyMessage);
    } finally {
        tagSelect.disabled = false;
    }
}

// 加载 Branches
async function loadBranches(repo) {
    branchSelect.disabled = true;
    branchSelect.innerHTML = '';

    try {
        const res = await fetch(`/api/branches?project_id=${selectedProjectId}`);
        if (!res.ok) {
            let errorMsg = '获取分支信息失败';
            if (res.status === 404) {
                errorMsg = '项目不存在或无法访问';
            } else if (res.status === 403) {
                errorMsg = 'API访问限制，请稍后再试';
            } else if (res.status >= 500) {
                errorMsg = '服务器内部错误，请稍后重试';
            }
            throw new Error(errorMsg);
        }
        const branches = await res.json();

        // 直接展示有效选项，无需占位符
        let hasValidBranches = false;

        if (branches.length > 0) {
            branches.slice(0, 30).forEach((branch, index) => {
                const opt = document.createElement('option');
                opt.value = branch.name;
                opt.textContent = branch.name;
                opt.style.color = '#2c3e50';

                branchSelect.appendChild(opt);

                // 默认选中优先级：master/main > 第一个分支
                if (branch.name === 'master' || branch.name === 'main' || (index === 0 && !hasValidBranches)) {
                    branchSelect.value = branch.name;
                    nextStep2Btn.disabled = false;
                    hasValidBranches = true;
                }
            });
        } else {
            // 无可用分支时不显示任何选项
            nextStep2Btn.disabled = true;
        }

        // 更新下一步按钮状态
        nextStep2Btn.disabled = !hasValidBranches;
    } catch (err) {
        // 错误状态下提供友好提示
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = '加载失败，请重试';
        opt.disabled = true;
        opt.style.color = '#dc3545';
        branchSelect.appendChild(opt);
        nextStep2Btn.disabled = true;

        let userFriendlyMessage = err.message;
        if (err.message.includes('fetch')) {
            userFriendlyMessage = '网络连接异常，请检查网络后重试';
        } else if (err.message.includes('Failed to fetch')) {
            userFriendlyMessage = '无法连接到服务器，请稍后重试';
        }

        showError('获取Branch失败', userFriendlyMessage);
    } finally {
        branchSelect.disabled = false;
    }
}

// 类型选择事件
document.querySelectorAll('.type-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
        // 更新按钮状态
        document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // 更新下载类型
        selectedProjectVersionType = btn.dataset.type;

        // 切换显示的选项组
        if (selectedProjectVersionType === 'tag') {
            tagGroup.style.display = 'block';
            branchGroup.style.display = 'none';
            nextStep2Btn.disabled = !tagSelect.value;
        } else {
            tagGroup.style.display = 'none';
            branchGroup.style.display = 'block';
            nextStep2Btn.disabled = !branchSelect.value;
        }

        // 重新加载对应类型的版本信息
        if (selectedRepo) {
            await loadVersions(selectedRepo);
        }
    });
});

// 监听选择变化
tagSelect.addEventListener('change', () => {
    nextStep2Btn.disabled = !tagSelect.value;
    if (tagSelect.value) {
        updateSelectedProjectInfo();
    }
});

branchSelect.addEventListener('change', () => {
    nextStep2Btn.disabled = !branchSelect.value;
    if (branchSelect.value) {
        updateSelectedProjectInfo();
    }
});

// Step 2 按钮
if (prevStep2Btn) prevStep2Btn.addEventListener('click', async () => await goToStep(1));
if (nextStep2Btn) nextStep2Btn.addEventListener('click', async () => {
    selectedProjectVersion = selectedProjectVersionType === 'tag' ? tagSelect.value : branchSelect.value;
    if (selectedProjectVersion) await goToStep(3);
});

// Step 3 按钮
if (prevStep3Btn) prevStep3Btn.addEventListener('click', async () => await goToStep(2));

// 显示错误提示
function showError(title, message) {
    // 移除已存在的错误模态框
    const existingModal = document.querySelector('.error-modal');
    if (existingModal) {
        existingModal.remove();
    }

    const modal = document.createElement('div');
    modal.className = 'error-modal';
    modal.innerHTML = `
        <div class="error-overlay"></div>
        <div class="error-container">
            <div class="error-card">
                <div class="error-decoration"></div>
                <div class="error-main">
                    <div class="error-graphic">
                        <div class="error-circle">
                            <div class="error-icon">⚠️</div>
                        </div>
                        <div class="error-waves">
                            <div class="wave"></div>
                            <div class="wave"></div>
                            <div class="wave"></div>
                        </div>
                    </div>
                    <div class="error-content">
                        <h3 class="error-title">${title}</h3>
                        <p class="error-message">${message}</p>
                        <div class="error-actions">
                            <button class="error-btn error-btn-primary" data-action="confirm">
                                <span class="btn-text">确定</span>
                                <span class="btn-icon">→</span>
                            </button>
                            <button class="error-btn error-btn-secondary" data-action="cancel">
                                <span class="btn-text">取消</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // 添加关闭事件
    const confirmBtn = modal.querySelector('[data-action="confirm"]');
    const cancelBtn = modal.querySelector('[data-action="cancel"]');
    const overlay = modal.querySelector('.error-overlay');

    const closeError = () => {
        modal.classList.add('error-modal-closing');
        // 添加轻微震动效果
        const card = modal.querySelector('.error-card');
        card.style.animation = 'shake 0.5s';
        setTimeout(() => {
            if (modal.parentNode) {
                modal.remove();
            }
        }, 300);
    };

    confirmBtn.addEventListener('click', closeError);
    cancelBtn.addEventListener('click', closeError);
    overlay.addEventListener('click', closeError);

    // 添加入场动画延迟
    setTimeout(() => {
        modal.classList.add('error-modal-visible');
    }, 50);

    // 自动聚焦到确认按钮
    setTimeout(() => {
        confirmBtn.focus();
    }, 300);
}

// 下载提交按钮点击事件
const submitBtn = document.querySelector('.submit-btn');
if (submitBtn) {
    submitBtn.addEventListener('click', async () => {
        // 获取表单数据
        const projectName = document.getElementById('projectName')?.value.trim();
        const packageName = document.getElementById('packageName')?.value.trim();
        const artifactId = document.getElementById('artifactId')?.value.trim();
        const groupId = document.getElementById('groupId')?.value.trim();
        const siteName = document.getElementById('siteName')?.value.trim();

        // 验证必填字段
        if (!selectedProjectId || !selectedProjectVersion || !projectName || !packageName || !artifactId || !groupId || !siteName) {
            showError('信息不完整', '请填写所有必填信息！');
            return;
        }

        // 验证包名格式
        if (!/^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$/.test(packageName)) {
            showError('包名格式错误', '包名应符合 Java 包名规范，如 com.company.project');
            return;
        }

        // 构造JSON数据
        const requestData = {
            id: selectedProjectId,
            version: selectedProjectVersion,
            version_type: selectedProjectVersionType,
            project_name: projectName,
            package_name: packageName,
            artifact_id: artifactId,
            group_id: groupId,
            site_name: siteName
        };

        // 禁用提交按钮
        const submitBtn = document.querySelector('.submit-btn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
            <span class="processing-spinner"></span>
            <span>处理中...</span>
        `;
        }

        try {
            // 发送JSON格式的POST请求
            const res = await fetch('/api/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            if (res.ok) {
                // 获取文件名
                const contentDisposition = res.headers.get('Content-Disposition');
                let filename = `${projectName}.zip`;
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                    if (filenameMatch) {
                        filename = filenameMatch[1];
                    }
                }

                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                showError('系统异常', '请稍后再试');
            }
        } catch (error) {
            showError('网络错误', '请检查网络连接后重试');
        }

        // 恢复提交按钮
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '下载';
        }
    });
}


// 页面加载完成后初始化
window.addEventListener('load', async () => {
    // 添加淡入动画
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease';
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);

    await loadProjects();
});