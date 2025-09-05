"""
CRUD Generator - 一键生成完整的CURD操作
基于实体配置，自动生成实体、仓库、Handler、路由和测试
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from loguru import logger
from dataclasses import dataclass


@dataclass
class FieldConfig:
    """字段配置"""
    name: str
    type: str
    required: bool = True
    unique: bool = False
    index: bool = False
    default: Any = None
    description: str = ""


@dataclass
class EntityConfig:
    """实体配置"""
    name: str
    table: str
    fields: List[FieldConfig]
    soft_delete: bool = True
    timestamps: bool = True
    description: str = ""


class CRUDGenerator:
    """CRUD代码生成器"""
    
    def __init__(self, project_path: Path, project_name: str):
        self.project_path = project_path
        self.project_name = project_name
        self.entities_path = project_path / "internal" / "entity"
        self.repos_path = project_path / "adapter" / "repo"  # 修正：Repository应该在外层(适配器层)
        self.handlers_path = project_path / "adapter" / "handler"
        self.routes_path = project_path / "pkg" / "http"
        self.tests_path = project_path / "test"
    
    def generate_from_config(self, config_path: Path):
        """从配置文件生成CRUD"""
        logger.info(f"📦 从配置文件生成CRUD: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        entities = self._parse_config(config)
        
        for entity_config in entities:
            self._generate_entity(entity_config)
            self._generate_repository(entity_config)
            self._generate_handler(entity_config)
            self._generate_routes(entity_config)
            self._generate_tests(entity_config)
            
        self._update_main_routes(entities)
        logger.success("✅ CRUD生成完成！")
    
    def generate_from_simple(self, entity_name: str, fields: Dict[str, str]):
        """简单模式生成CRUD"""
        logger.info(f"🚀 简单模式生成CRUD: {entity_name}")
        
        entity_config = EntityConfig(
            name=entity_name.capitalize(),
            table=entity_name.lower() + "s",
            fields=[
                FieldConfig(name="id", type="uint", description="主键ID"),
                *[FieldConfig(name=k, type=v) for k, v in fields.items()],
                FieldConfig(name="created_at", type="time.Time", description="创建时间"),
                FieldConfig(name="updated_at", type="time.Time", description="更新时间"),
            ],
            description=f"{entity_name}实体"
        )
        
        self._generate_entity(entity_config)
        self._generate_repository(entity_config)
        self._generate_handler(entity_config)
        self._generate_routes(entity_config)
        self._generate_tests(entity_config)
        
        logger.success(f"✅ {entity_name} CRUD生成完成！")
    
    def _parse_config(self, config: Dict[str, Any]) -> List[EntityConfig]:
        """解析配置文件"""
        entities = []
        
        for entity_data in config.get('entities', []):
            fields = []
            for field_data in entity_data.get('fields', []):
                fields.append(FieldConfig(
                    name=field_data['name'],
                    type=field_data['type'],
                    required=field_data.get('required', True),
                    unique=field_data.get('unique', False),
                    index=field_data.get('index', False),
                    default=field_data.get('default'),
                    description=field_data.get('description', '')
                ))
            
            entities.append(EntityConfig(
                name=entity_data['name'],
                table=entity_data.get('table', entity_data['name'].lower() + "s"),
                fields=fields,
                soft_delete=entity_data.get('soft_delete', True),
                timestamps=entity_data.get('timestamps', True),
                description=entity_data.get('description', '')
            ))
        
        return entities
    
    def _generate_entity(self, config: EntityConfig):
        """生成实体代码"""
        entity_code = self._build_entity_code(config)
        entity_file = self.entities_path / f"{config.name.lower()}.go"
        entity_file.write_text(entity_code)
        logger.success(f"✅ 生成实体: {entity_file}")
    
    def _generate_repository(self, config: EntityConfig):
        """生成仓库代码"""
        repo_code = self._build_repository_code(config)
        repo_file = self.repos_path / f"{config.name.lower()}_repo.go"
        repo_file.write_text(repo_code)
        logger.success(f"✅ 生成仓库: {repo_file}")
    
    def _generate_handler(self, config: EntityConfig):
        """生成Handler代码"""
        handler_code = self._build_handler_code(config)
        handler_file = self.handlers_path / f"{config.name.lower()}_handler.go"
        handler_file.write_text(handler_code)
        logger.success(f"✅ 生成Handler: {handler_file}")
    
    def _generate_routes(self, config: EntityConfig):
        """生成路由代码"""
        route_code = self._build_routes_code(config)
        route_file = self.routes_path / f"{config.name.lower()}_routes.go"
        route_file.write_text(route_code)
        logger.success(f"✅ 生成路由: {route_file}")
    
    def _generate_tests(self, config: EntityConfig):
        """生成测试代码"""
        test_code = self._build_test_code(config)
        test_file = self.tests_path / f"{config.name.lower()}_test.go"
        test_file.write_text(test_code)
        logger.success(f"✅ 生成测试: {test_file}")
    
    def _update_main_routes(self, entities: List[EntityConfig]):
        """更新主路由注册"""
        # 这里可以添加路由注册代码
        pass
    
    def _build_entity_code(self, config: EntityConfig) -> str:
        """构建实体代码"""
        fields_code = ""
        for field in config.fields:
            tag = f'`json:"{field.name}" gorm:"'
            if field.name == "id":
                tag += 'primaryKey;autoIncrement"'
            else:
                tags = []
                if field.unique:
                    tags.append("unique")
                if field.index:
                    tags.append("index")
                if field.name.endswith("_at"):
                    tags.append("autoCreateTime")
                tag += ";".join(tags) + '"'
            tag += '`'
            
            fields_code += f"\t{field.name.capitalize()} {field.type} {tag} // {field.description}\n"
        
        return f"""package entity

import "time"

// {config.name} {config.description}
type {config.name} struct {{
{fields_code}}}
"""
    
    def _build_repository_code(self, config: EntityConfig) -> str:
        """构建仓库代码"""
        name_lower = config.name.lower()
        name_upper = config.name
        
        return f"""package repo

import (
	"context"
	"{self.project_name}/internal/entity"
	"gorm.io/gorm"
)

// {name_upper}Repository {config.description}仓库
type {name_upper}Repository struct {{
	db *gorm.DB
}}

// New{name_upper}Repository 创建{name_upper}仓库
func New{name_upper}Repository(db *gorm.DB) *{name_upper}Repository {{
	return &{name_upper}Repository{{db: db}}
}}

// Create 创建{name_upper}
func (r *{name_upper}Repository) Create(ctx context.Context, {name_lower} *entity.{name_upper}) error {{
	return r.db.WithContext(ctx).Create({name_lower}).Error
}}

// GetByID 根据ID获取{name_upper}
func (r *{name_upper}Repository) GetByID(ctx context.Context, id uint) (*entity.{name_upper}, error) {{
	var {name_lower} entity.{name_upper}
	err := r.db.WithContext(ctx).First(&{name_lower}, id).Error
	if err != nil {{
		return nil, err
	}}
	return &{name_lower}, nil
}}

// List 获取{name_upper}列表
func (r *{name_upper}Repository) List(ctx context.Context, limit, offset int) ([]*entity.{name_upper}, error) {{
	var {name_lower}s []*entity.{name_upper}
	err := r.db.WithContext(ctx).Limit(limit).Offset(offset).Find(&{name_lower}s).Error
	return {name_lower}s, err
}}

// Update 更新{name_upper}
func (r *{name_upper}Repository) Update(ctx context.Context, {name_lower} *entity.{name_upper}) error {{
	return r.db.WithContext(ctx).Save({name_lower}).Error
}}

// Delete 删除{name_upper}
func (r *{name_upper}Repository) Delete(ctx context.Context, id uint) error {{
	return r.db.WithContext(ctx).Delete(&entity.{name_upper}{{ID: id}}).Error
}}
"""
    
    def _build_handler_code(self, config: EntityConfig) -> str:
        """构建Handler代码"""
        name_lower = config.name.lower()
        name_upper = config.name
        
        return f"""package handler

import (
	"net/http"
	"strconv"
	"{self.project_name}/internal/entity"
	"{self.project_name}/adapter/repo"
	"github.com/gin-gonic/gin"
)

// {name_upper}Handler {config.description}处理器
type {name_upper}Handler struct {{
	{name_lower}Repo *repo.{name_upper}Repository
}}

// New{name_upper}Handler 创建{name_upper}处理器
func New{name_upper}Handler({name_lower}Repo *repo.{name_upper}Repository) *{name_upper}Handler {{
	return &{name_upper}Handler{{ {name_lower}Repo: {name_lower}Repo }}
}}

// Create 创建{name_upper}
// @Summary 创建{name_upper}
// @Description 创建一个新的{name_upper}
// @Accept json
// @Produce json
// @Param {name_lower} body entity.{name_upper} true "{name_upper}信息"
// @Success 201 {{object}} entity.{name_upper}
// @Failure 400 {{object}} map[string]string
// @Router /api/v1/{name_lower}s [post]
func (h *{name_upper}Handler) Create(c *gin.Context) {{
	var {name_lower} entity.{name_upper}
	if err := c.ShouldBindJSON(&{name_lower}); err != nil {{
		c.JSON(http.StatusBadRequest, gin.H{{"error": err.Error()}})
		return
	}}

	if err := h.{name_lower}Repo.Create(c.Request.Context(), &{name_lower}); err != nil {{
		c.JSON(http.StatusInternalServerError, gin.H{{"error": err.Error()}})
		return
	}}

	c.JSON(http.StatusCreated, {name_lower})
}}

// Get 获取{name_upper}详情
// @Summary 获取{name_upper}详情
// @Description 根据ID获取{name_upper}详情
// @Produce json
// @Param id path int true "{name_upper}ID"
// @Success 200 {{object}} entity.{name_upper}
// @Failure 404 {{object}} map[string]string
// @Router /api/v1/{name_lower}s/{id} [get]
func (h *{name_upper}Handler) Get(c *gin.Context) {{
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {{
		c.JSON(http.StatusBadRequest, gin.H{{"error": "无效的ID"}})
		return
	}}

	{name_lower}, err := h.{name_lower}Repo.GetByID(c.Request.Context(), uint(id))
	if err != nil {{
		c.JSON(http.StatusNotFound, gin.H{{"error": "{name_upper}不存在"}})
		return
	}}

	c.JSON(http.StatusOK, {name_lower})
}}

// List 获取{name_upper}列表
// @Summary 获取{name_upper}列表
// @Description 获取{name_upper}分页列表
// @Produce json
// @Param page query int false "页码" default(1)
// @Param limit query int false "每页数量" default(10)
// @Success 200 {{object}} map[string]interface{{}}
// @Router /api/v1/{name_lower}s [get]
func (h *{name_upper}Handler) List(c *gin.Context) {{
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "10"))
	if page < 1 {{
		page = 1
	}}
	if limit < 1 || limit > 100 {{
		limit = 10
	}}

	{name_lower}s, err := h.{name_lower}Repo.List(c.Request.Context(), limit, (page-1)*limit)
	if err != nil {{
		c.JSON(http.StatusInternalServerError, gin.H{{"error": err.Error()}})
		return
	}}

	c.JSON(http.StatusOK, gin.H{{
		"data": {name_lower}s,
		"page": page,
		"limit": limit,
	}})
}}

// Update 更新{name_upper}
// @Summary 更新{name_upper}
// @Description 更新{name_upper}信息
// @Accept json
// @Produce json
// @Param id path int true "{name_upper}ID"
// @Param {name_lower} body entity.{name_upper} true "{name_upper}信息"
// @Success 200 {{object}} entity.{name_upper}
// @Failure 400 {{object}} map[string]string
// @Router /api/v1/{name_lower}s/{id} [put]
func (h *{name_upper}Handler) Update(c *gin.Context) {{
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {{
		c.JSON(http.StatusBadRequest, gin.H{{"error": "无效的ID"}})
		return
	}}

	var {name_lower} entity.{name_upper}
	if err := c.ShouldBindJSON(&{name_lower}); err != nil {{
		c.JSON(http.StatusBadRequest, gin.H{{"error": err.Error()}})
		return
	}}

	{name_lower}.ID = uint(id)
	if err := h.{name_lower}Repo.Update(c.Request.Context(), &{name_lower}); err != nil {{
		c.JSON(http.StatusInternalServerError, gin.H{{"error": err.Error()}})
		return
	}}

	c.JSON(http.StatusOK, {name_lower})
}}

// Delete 删除{name_upper}
// @Summary 删除{name_upper}
// @Description 删除{name_upper}
// @Param id path int true "{name_upper}ID"
// @Success 204 {{object}} map[string]string
// @Failure 400 {{object}} map[string]string
// @Router /api/v1/{name_lower}s/{id} [delete]
func (h *{name_upper}Handler) Delete(c *gin.Context) {{
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {{
		c.JSON(http.StatusBadRequest, gin.H{{"error": "无效的ID"}})
		return
	}}

	if err := h.{name_lower}Repo.Delete(c.Request.Context(), uint(id)); err != nil {{
		c.JSON(http.StatusInternalServerError, gin.H{{"error": err.Error()}})
		return
	}}

	c.JSON(http.StatusNoContent, gin.H{{"message": "删除成功"}})
}}
"""
    
    def _build_routes_code(self, config: EntityConfig) -> str:
        """构建路由代码"""
        name_lower = config.name.lower()
        name_upper = config.name
        
        return f"""package http

import (
	"{self.project_name}/adapter/handler"
	"{self.project_name}/internal/repo"
	"gorm.io/gorm"
	"github.com/gin-gonic/gin"
)

// Register{name_upper}Routes 注册{name_upper}路由
func Register{name_upper}Routes(router *gin.RouterGroup, db *gorm.DB) {{
	{name_lower}Repo := repo.New{name_upper}Repository(db)
	{name_lower}Handler := handler.New{name_upper}Handler({name_lower}Repo)

	{name_lower}s := router.Group("/{name_lower}s")
	{{
		{name_lower}s.POST("", {name_lower}Handler.Create)
		{name_lower}s.GET("", {name_lower}Handler.List)
		{name_lower}s.GET("/:id", {name_lower}Handler.Get)
		{name_lower}s.PUT("/:id", {name_lower}Handler.Update)
		{name_lower}s.DELETE("/:id", {name_lower}Handler.Delete)
	}}
}}
"""
    
    def _build_test_code(self, config: EntityConfig) -> str:
        """构建测试代码"""
        name_lower = config.name.lower()
        name_upper = config.name
        
        return f"""package test

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"{self.project_name}/internal/entity"
	"github.com/stretchr/testify/assert"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

func setupTestDB() *gorm.DB {{
	db, _ := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{{}})
	db.AutoMigrate(&entity.{name_upper}{{}})
	return db
}}

func Test{name_upper}CRUD(t *testing.T) {{
	db := setupTestDB()
	assert.NotNil(t, db)

	// 测试创建
	{name_lower} := &entity.{name_upper}{{
		// TODO: 填充测试数据
	}}

	result := db.Create({name_lower})
	assert.NoError(t, result.Error)
	assert.Greater(t, {name_lower}.ID, uint(0))

	// 测试查询
	var found entity.{name_upper}
	err := db.First(&found, {name_lower}.ID).Error
	assert.NoError(t, err)
	assert.Equal(t, {name_lower}.ID, found.ID)

	// 测试更新
	// TODO: 添加更新测试

	// 测试删除
	err = db.Delete(&entity.{name_upper}{{ID: {name_lower}.ID}}).Error
	assert.NoError(t, err)
}}

func Test{name_upper}API(t *testing.T) {{
	// TODO: 添加API测试
}}
"""