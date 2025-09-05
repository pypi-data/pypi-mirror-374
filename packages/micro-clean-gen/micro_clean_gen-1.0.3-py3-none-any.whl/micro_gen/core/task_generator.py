#!/usr/bin/env python3
"""
任务机制生成器
为项目添加长时处理任务机制和定时任务机制
"""

from pathlib import Path
from typing import Dict, Any, List

from .base_generator import BaseGenerator


class TaskGenerator(BaseGenerator):
    """任务机制生成器"""
    
    def __init__(self, project_path: Path, config: Dict[str, Any] = None):
        """初始化任务生成器
        
        Args:
            project_path: 项目根目录
            config: 项目配置
        """
        super().__init__(project_path, config)
    
    def generate(self) -> None:
        """生成任务机制代码"""
        # 创建目录结构
        self._create_directories()
        
        # 生成文件
        self._generate_entity()
        self._generate_store()
        self._generate_redis_store()
        self._generate_badger_store()
        self._generate_usecase()
        self._generate_manager()
        self._generate_example()
        
        # 更新配置
        self._update_config()
    
    def _create_directories(self) -> None:
        """创建任务相关目录"""
        directories = [
            Path("pkg/task"),
            Path("internal/usecase/task"),
            Path("internal/entity"),
        ]
        self.create_directories(directories)
    
    def _generate_entity(self) -> None:
        """生成任务实体"""
        content = self.render_template("task", "entity_task.go.tmpl")
        self.generate_file(Path("internal/entity/task_data.go"), content)
    
    def _generate_store(self) -> None:
        """生成任务存储接口"""
        content = self.render_template("task", "task_store.go.tmpl")
        self.generate_file(Path("pkg/task/task_store.go"), content)
    
    def _generate_redis_store(self) -> None:
        """生成Redis存储实现"""
        content = self.render_template("task", "redis_store.go.tmpl")
        self.generate_file(Path("pkg/task/redis_store.go"), content)
    
    def _generate_badger_store(self) -> None:
        """生成Badger存储实现"""
        content = self.render_template("task", "badger_store.go.tmpl")
        self.generate_file(Path("pkg/task/badger_store.go"), content)
    
    def _generate_usecase(self) -> None:
        """生成任务服务用例"""
        content = self.render_template("task", "usecase_task.go.tmpl")
        self.generate_file(Path("internal/usecase/task/usecase_task.go"), content)
    
    def _generate_manager(self) -> None:
        """生成任务管理器"""
        content = self.render_template("task", "task_manager.go.tmpl")
        self.generate_file(Path("pkg/task/task_manager.go"), content)
    
    def _generate_example(self) -> None:
        """生成使用示例"""
        content = self.render_template("task", "example_usage.go.tmpl")
        self.generate_file(Path("pkg/task/example_usage.go"), content)
    
    def _update_config(self) -> None:
        """更新配置文件"""
        config_file = self.project_path / "pkg" / "config" / "config.go"
        if not config_file.exists():
            return
        
        # 读取现有内容
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"读取配置文件失败: {e}")
            return
        
        # 添加任务配置
        task_config = """
	// 任务配置
	TaskLevel    string `yaml:"task_level" env:"TASK_LEVEL" env-default:"low"`
	TaskTimeout  int    `yaml:"task_timeout" env:"TASK_TIMEOUT" env-default:"30"` // 分钟
	TaskWorkers  int    `yaml:"task_workers" env:"TASK_WORKERS" env-default:"3"`
	TaskRetries  int    `yaml:"task_retries" env:"TASK_RETRIES" env-default:"3"`
"""
        
        # 检查是否已存在任务配置
        if 'TaskLevel' in content:
            return
        
        # 查找结构体定义结束位置
        lines = content.split('\n')
        new_lines = []
        added = False
        
        for line in lines:
            new_lines.append(line)
            
            # 在结构体最后一个字段后添加任务配置
            if not added and line.strip().endswith('`') and 'type Config struct' in content:
                # 找到结构体结束位置
                brace_count = 0
                in_struct = False
                
                for i, l in enumerate(lines):
                    if 'type Config struct' in l:
                        in_struct = True
                        brace_count = 1
                    elif in_struct:
                        if '{' in l:
                            brace_count += l.count('{')
                        if '}' in l:
                            brace_count -= l.count('}')
                            if brace_count == 0:
                                # 在结构体结束前添加任务配置
                                new_lines = lines[:i] + [task_config.strip()] + lines[i:]
                                added = True
                                break
        
        if added:
            new_content = '\n'.join(new_lines)
            try:
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            except Exception as e:
                logger.warning(f"更新配置文件失败: {e}")
    
    def get_instructions(self) -> List[str]:
        """获取使用说明"""
        return [
            "🚀 任务机制添加完成！",
            "",
            "📁 生成的文件:",
            "   • 实体定义: internal/entity/task_data.go",
            "   • 任务存储: pkg/task/task_store.go",
            "   • Redis存储: pkg/task/redis_store.go",
            "   • Badger存储: pkg/task/badger_store.go",
            "   • 任务服务: internal/usecase/task/usecase_task.go",
            "   • 任务管理器: pkg/task/task_manager.go",
            "   • 使用示例: pkg/task/example_usage.go",
            "",
            "🔧 下一步:",
            "   1. 安装依赖:",
            "      go get github.com/redis/go-redis/v9",
            "      go get github.com/dgraph-io/badger/v4",
            "      go get github.com/robfig/cron/v3",
            "",
            "   2. 配置任务存储:",
            "      设置环境变量 TASK_LEVEL=low|normal|high",
            "      TASK_LEVEL=low (内存存储) - 开发/测试环境",
            "      TASK_LEVEL=normal (Badger存储) - 中小型项目",
            "      TASK_LEVEL=high (Redis存储) - 大型项目",
            "",
            "   3. 使用任务管理器:",
            "      查看 pkg/task/example_usage.go 了解使用方法",
            "",
            "   4. 任务类型示例:",
            "      • email_notification - 邮件通知",
            "      • report_generation - 报告生成",
            "      • data_cleanup - 数据清理",
            "      • backup_database - 数据库备份",
            "      • sync_data - 数据同步",
            "",
            "   5. 定时任务配置:",
            "      使用 cron 表达式设置定时任务",
            "      例如: '0 2 * * *' 每天凌晨2点执行"
        ]